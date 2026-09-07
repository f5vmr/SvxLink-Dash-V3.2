#!/usr/bin/env python3

import unittest
from unittest.mock import patch

from renderers.svxlink_renderer import (
    render_port_tx_ctcss_logic,
    render_port_tx_section,
    render_tx_ctcss_block,
    render_tx_ctcss_logic,
    render_transmitter_common_options,
)


class TransmitterRenderingTests(unittest.TestCase):

    def make_model(self, family="usb_multi_interface"):
        return {
            "hardware": {
                "family": family,
            },
        }

    def make_node(
        self,
        sql_method="ctcss",
        ptt_source=None,
    ):
        node = {
            "audio": {
                "tx_audio": "alsa:plughw:0",
                "preemphasis": False,
            },
            "squelch": {
                "method": sql_method,
                "ctcss_freq": (
                    "88.5"
                    if sql_method == "ctcss"
                    else None
                ),
            },
            "gpio": {
                "ptt_invert": False,
            },
            "hidraw": {
                "device": "/dev/hidraw3",
                "ptt_pin": "GPIO3",
                "ptt_invert": False,
            },
            "serial": {
                "ptt_port": "/dev/ttyUSB1",
                "ptt_pin": "RTS",
            },
        }

        if ptt_source is not None:
            node["interface"] = {
                "ptt_source": ptt_source,
            }

        return node

    def test_ctcss_sql_can_use_hidraw_ptt(self):
        rendered = render_port_tx_section(
            self.make_model(),
            "1",
            self.make_node(
                sql_method="ctcss",
                ptt_source="hidraw",
            ),
        )

        self.assertIn(
            "PTT_TYPE=Hidraw",
            rendered,
        )
        self.assertIn(
            "HID_DEVICE=/dev/hidraw3",
            rendered,
        )
        self.assertIn(
            "HID_PTT_PIN=GPIO3",
            rendered,
        )
        self.assertNotIn(
            "PTT_TYPE=GPIOD",
            rendered,
        )

    def test_ctcss_sql_can_use_serial_ptt(self):
        rendered = render_port_tx_section(
            self.make_model(),
            "1",
            self.make_node(
                sql_method="ctcss",
                ptt_source="serial",
            ),
        )

        self.assertIn(
            "PTT_TYPE=SerialPin",
            rendered,
        )
        self.assertIn(
            "PTT_PORT=/dev/ttyUSB1",
            rendered,
        )
        self.assertIn(
            "PTT_PIN=RTS",
            rendered,
        )
        self.assertNotIn(
            "PTT_TYPE=GPIOD",
            rendered,
        )

    def test_legacy_serial_pairing_is_preserved(self):
        rendered = render_port_tx_section(
            self.make_model(),
            "1",
            self.make_node(
                sql_method="serial",
            ),
        )

        self.assertIn(
            "PTT_TYPE=SerialPin",
            rendered,
        )

    def test_ics_ptt_remains_gpiod(self):
        node = self.make_node(
            sql_method="ctcss",
            ptt_source="hidraw",
        )

        with patch(
            "renderers.svxlink_renderer."
            "resolve_gpiod_line",
            return_value={
                "chip": "gpiochip4",
                "line": "TX_1",
            },
        ):
            rendered = render_port_tx_section(
                self.make_model("ics"),
                "1",
                node,
            )

        self.assertIn(
            "PTT_TYPE=GPIOD",
            rendered,
        )
        self.assertIn(
            "PTT_GPIOD_CHIP=gpiochip4",
            rendered,
        )
        self.assertIn(
            "PTT_GPIOD_LINE=!TX_1",
            rendered,
        )
        self.assertNotIn(
        """_summary_
        """            "PTT_TYPE=Hidraw",
            rendered,
        )
        self.assertNotIn(
            "PTT_TYPE=SerialPin",
            rendered,
        )

    def test_single_port_optional_tx_ctcss(self):
        model = {
            "squelch": {
                "method": "ctcss",
                "ctcss_freq": "88.5",
                "ctcss_tx": True,
            },
        }

        self.assertEqual(
            render_tx_ctcss_logic(model),
            "TX_CTCSS=ALWAYS",
        )
        self.assertEqual(
            render_tx_ctcss_block(model),
            "\n".join([
                "CTCSS_FQ=88.5",
                "CTCSS_LEVEL=-24",
            ]),
        )

    def test_single_port_receive_only_ctcss(self):
        model = {
            "squelch": {
                "method": "ctcss",
                "ctcss_freq": "88.5",
                "ctcss_tx": False,
            },
        }

        self.assertEqual(
            render_tx_ctcss_logic(model),
            "#TX_CTCSS=ALWAYS",
        )
        self.assertEqual(
            render_tx_ctcss_block(model),
            "",
        )

    def test_multiport_optional_tx_ctcss(self):
        node = self.make_node(
            sql_method="ctcss",
            ptt_source="gpiod",
        )
        node["squelch"]["ctcss_tx"] = True

        with patch(
            "renderers.svxlink_renderer."
            "resolve_gpiod_line",
            return_value={
                "chip": "gpiochip4",
                "line": "TX_1",
            },
        ):
            rendered = render_port_tx_section(
                self.make_model(),
                "1",
                node,
            )

        self.assertEqual(
            render_port_tx_ctcss_logic(node),
            "TX_CTCSS=ALWAYS",
        )
        self.assertIn(
            "CTCSS_FQ=88.5",
            rendered,
        )
        self.assertIn(
            "CTCSS_LEVEL=-24",
            rendered,
        )
        self.assertNotIn(
            "CTCSS_LEVEL=9",
            rendered,
        )

    def test_non_ctcss_sql_cannot_render_tx_ctcss(self):
        node = self.make_node(
            sql_method="hidraw",
            ptt_source="hidraw",
        )
        node["squelch"]["ctcss_freq"] = "88.5"
        node["squelch"]["ctcss_tx"] = True

        rendered = render_port_tx_section(
            self.make_model(),
            "1",
            node,
        )

        self.assertEqual(
            render_port_tx_ctcss_logic(node),
            "#TX_CTCSS=ALWAYS",
        )
        self.assertNotIn(
            "CTCSS_FQ=",
            rendered,
        )
        self.assertNotIn(
            "CTCSS_LEVEL=",
            rendered,
        )

    def test_multiport_tx_delay(self):
        node = self.make_node(
            sql_method="hidraw",
            ptt_source="hidraw",
        )
        node["tx_delay"] = 275

        rendered = render_port_tx_section(
            self.make_model(),
            "1",
            node,
        )

        self.assertIn(
            "TX_DELAY=275",
            rendered,
        )

    def test_multiport_tx_delay_defaults_to_500(self):
        node = self.make_node(
            sql_method="hidraw",
            ptt_source="hidraw",
        )

        rendered = render_port_tx_section(
            self.make_model(),
            "1",
            node,
        )

        self.assertIn(
            "TX_DELAY=500",
            rendered,
        )

    def test_common_manual_transmitter_options(self):
        rendered = (
            render_transmitter_common_options(
                "Tx1"
            )
        )

        for expected in (
            "#DTMF_TONE_LENGTH=100",
            "#DTMF_TONE_SPACING=50",
            "#DTMF_DIGIT_PWR=-15",
            "#MASTER_GAIN=0.0",
            "#OB_AFSK_ENABLE=0",
            "#IB_AFSK_ENABLE=0",
            "#LADSPA_PLUGINS=hpf:1000,@Tx1_Compressor",
            "#[Tx1_Compressor]",
        ):
            with self.subTest(expected=expected):
                self.assertIn(
                    expected,
                    rendered,
                )

        self.assertNotIn(
            "\nDTMF_TONE_LENGTH=",
            "\n" + rendered,
        )

    def test_multiport_retains_tx_structure(self):
        node = self.make_node(
            sql_method="hidraw",
            ptt_source="hidraw",
        )
        node["tx_delay"] = 500
        node["audio"]["preemphasis"] = True

        rendered = render_port_tx_section(
            self.make_model(),
            "2",
            node,
        )

        for expected in (
            "TYPE=Local",
            "#TX_ID=T",
            "AUDIO_CHANNEL=0",
            "#AUDIO_DEV_KEEP_OPEN=0",
            "#LIMITER_THRESH=-6",
            "#PTT_HANGTIME=1000",
            "#TIMEOUT=0",
            "#GPIO_PATH=/sys/class/gpio",
            "TX_DELAY=500",
            "PREEMPHASIS=1",
            "#[Tx2_Compressor]",
        ):
            with self.subTest(expected=expected):
                self.assertIn(
                    expected,
                    rendered,
                )

        self.assertEqual(
            rendered.count("PREEMPHASIS="),
            1,
        )

if __name__ == "__main__":
    unittest.main()

"""Offline safety-contract tests for printer controls."""

import json
import unittest

from tools.qidi_q2 import printer


class FakeClient:
    def __init__(self):
        self.commands = []

    def gcode(self, command):
        self.commands.append(command)
        return {}


class PrinterSafetyTests(unittest.TestCase):
    def assert_rejected_without_command(self, result, client):
        payload = json.loads(result)
        self.assertFalse(payload["success"])
        self.assertEqual([], client.commands)

    def test_speed_rejects_values_outside_documented_range(self):
        for value in (49, 201):
            with self.subTest(value=value):
                client = FakeClient()
                self.assert_rejected_without_command(
                    printer.set_print_speed(value, client), client
                )
        client = FakeClient()
        self.assertEqual(
            "Print speed set to 200%",
            printer.set_print_speed(200, client),
        )
        self.assertEqual(["M220 S200"], client.commands)

    def test_flow_rejects_values_outside_documented_range(self):
        for value in (89, 111):
            with self.subTest(value=value):
                client = FakeClient()
                self.assert_rejected_without_command(
                    printer.set_flow_rate(value, client), client
                )
        client = FakeClient()
        self.assertEqual(
            "Flow rate set to 90%",
            printer.set_flow_rate(90, client),
        )
        self.assertEqual(["M221 S90"], client.commands)

    def test_temperature_uses_heater_specific_limits(self):
        cases = (("hotend", -1), ("hotend", 301), ("bed", -1), ("bed", 121))
        for heater, value in cases:
            with self.subTest(heater=heater, value=value):
                client = FakeClient()
                self.assert_rejected_without_command(
                    printer.set_temperature(heater, value, client), client
                )

        hotend = FakeClient()
        self.assertEqual(
            "Hotend target set to 300°C",
            printer.set_temperature("hotend", 300, hotend),
        )
        self.assertEqual(["M104 S300"], hotend.commands)

        bed = FakeClient()
        self.assertEqual(
            "Bed target set to 120°C",
            printer.set_temperature("bed", 120, bed),
        )
        self.assertEqual(["M140 S120"], bed.commands)

    def test_fan_rejects_values_outside_zero_to_one_hundred(self):
        for value in (-1, 101):
            with self.subTest(value=value):
                client = FakeClient()
                self.assert_rejected_without_command(
                    printer.set_fan_speed(value, client), client
                )
        client = FakeClient()
        self.assertEqual("Part fan set to 100%", printer.set_fan_speed(100, client))
        self.assertEqual(["M106 S255"], client.commands)

    def test_homing_rejects_unrecognized_or_repeated_axes(self):
        for axes in ("", "A", "XX", "X Y", "G28"):
            with self.subTest(axes=axes):
                client = FakeClient()
                self.assert_rejected_without_command(
                    printer.home_axes(axes, client), client
                )
        client = FakeClient()
        self.assertEqual("Homing XY", printer.home_axes("xy", client))
        self.assertEqual(["G28 XY"], client.commands)


if __name__ == "__main__":
    unittest.main()

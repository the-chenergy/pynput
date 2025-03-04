# coding=utf-8
# pynput
# Copyright (C) 2015-2022 Moses Palmér
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
The keyboard implementation for *macOS*.
"""

# pylint: disable=C0111
# The documentation is extracted from the base classes

# pylint: disable=R0903
# We implement stubs

import enum

import Quartz

from pynput._util.darwin import (
    get_unicode_to_keycode_map,
    keycode_context,
    ListenerMixin)
from pynput._util.darwin_vks import SYMBOLS
from . import _base


# From hidsystem/ev_keymap.h
NX_KEYTYPE_PLAY = 16
NX_KEYTYPE_MUTE = 7
NX_KEYTYPE_SOUND_DOWN = 1
NX_KEYTYPE_SOUND_UP = 0
NX_KEYTYPE_NEXT = 17
NX_KEYTYPE_PREVIOUS = 18

# pylint: disable=C0103; We want to use the names from the C API
# This is undocumented, but still widely known
kSystemDefinedEventMediaKeysSubtype = 8

# We extract this here since the name is very long
otherEventWithType = getattr(
        Quartz.NSEvent,
        'otherEventWithType_'
        'location_'
        'modifierFlags_'
        'timestamp_'
        'windowNumber_'
        'context_'
        'subtype_'
        'data1_'
        'data2_')
# pylint: enable=C0103


class KeyCode(_base.KeyCode):
    _PLATFORM_EXTENSIONS = (
        # Whether this is a media key
        '_is_media',
    )

    # Be explicit about fields
    _is_media = None

    @classmethod
    def _from_media(cls, vk, **kwargs):
        """Creates a media key from a key code.

        :param int vk: The key code.

        :return: a key code
        """
        return cls.from_vk(vk, _is_media=True, **kwargs)

    def _event(self, modifiers, mapping, is_pressed):
        """This key as a *Quartz* event.

        :param set modifiers: The currently active modifiers.

        :param mapping: The current keyboard mapping.

        :param bool is_press: Whether to generate a press event.

        :return: a *Quartz* event
        """
        vk = self.vk or mapping.get(self.char)
        if self._is_media:
            result = otherEventWithType(
                Quartz.NSSystemDefined,
                (0, 0),
                0xa00 if is_pressed else 0xb00,
                0,
                0,
                0,
                8,
                (self.vk << 16) | ((0xa if is_pressed else 0xb) << 8),
                -1).CGEvent()
        else:
            result = Quartz.CGEventCreateKeyboardEvent(
                None, 0 if vk is None else vk, is_pressed)

        Quartz.CGEventSetFlags(
            result,
            0
            | (Quartz.kCGEventFlagMaskAlternate
               if Key.alt in modifiers else 0)

            | (Quartz.kCGEventFlagMaskCommand
               if Key.cmd in modifiers else 0)

            | (Quartz.kCGEventFlagMaskControl
               if Key.ctrl in modifiers else 0)

            | (Quartz.kCGEventFlagMaskShift
               if Key.shift in modifiers else 0)

            | (Quartz.kCGEventFlagMaskSecondaryFn
               if Key.fn in modifiers else 0))

        if vk is None and self.char is not None:
            Quartz.CGEventKeyboardSetUnicodeString(
                result, len(self.char), self.char)

        return result


# pylint: disable=W0212
class Key(enum.Enum):
    # Default keys
    alt = KeyCode.from_vk(0x3A)
    alt_l = KeyCode.from_vk(0x3A)
    alt_r = KeyCode.from_vk(0x3D)
    alt_gr = KeyCode.from_vk(0x3D)
    backspace = KeyCode.from_vk(0x33)
    caps_lock = KeyCode.from_vk(0x39)
    cmd = KeyCode.from_vk(0x37)
    cmd_l = KeyCode.from_vk(0x37)
    cmd_r = KeyCode.from_vk(0x36)
    ctrl = KeyCode.from_vk(0x3B)
    ctrl_l = KeyCode.from_vk(0x3B)
    ctrl_r = KeyCode.from_vk(0x3E)
    delete = KeyCode.from_vk(0x75)
    down = KeyCode.from_vk(0x7D)
    end = KeyCode.from_vk(0x77)
    enter = KeyCode.from_vk(0x24)
    esc = KeyCode.from_vk(0x35)
    f1 = KeyCode.from_vk(0x7A)
    f2 = KeyCode.from_vk(0x78)
    f3 = KeyCode.from_vk(0x63)
    f4 = KeyCode.from_vk(0x76)
    f5 = KeyCode.from_vk(0x60)
    f6 = KeyCode.from_vk(0x61)
    f7 = KeyCode.from_vk(0x62)
    f8 = KeyCode.from_vk(0x64)
    f9 = KeyCode.from_vk(0x65)
    f10 = KeyCode.from_vk(0x6D)
    f11 = KeyCode.from_vk(0x67)
    f12 = KeyCode.from_vk(0x6F)
    f13 = KeyCode.from_vk(0x69)
    f14 = KeyCode.from_vk(0x6B)
    f15 = KeyCode.from_vk(0x71)
    f16 = KeyCode.from_vk(0x6A)
    f17 = KeyCode.from_vk(0x40)
    f18 = KeyCode.from_vk(0x4F)
    f19 = KeyCode.from_vk(0x50)
    f20 = KeyCode.from_vk(0x5A)
    home = KeyCode.from_vk(0x73)
    left = KeyCode.from_vk(0x7B)
    page_down = KeyCode.from_vk(0x79)
    page_up = KeyCode.from_vk(0x74)
    right = KeyCode.from_vk(0x7C)
    shift = KeyCode.from_vk(0x38)
    shift_l = KeyCode.from_vk(0x38)
    shift_r = KeyCode.from_vk(0x3C)
    space = KeyCode.from_vk(0x31, char=' ')
    tab = KeyCode.from_vk(0x30)
    up = KeyCode.from_vk(0x7E)
    fn = KeyCode.from_vk(0x3F)

    media_play_pause = KeyCode._from_media(NX_KEYTYPE_PLAY)
    media_volume_mute = KeyCode._from_media(NX_KEYTYPE_MUTE)
    media_volume_down = KeyCode._from_media(NX_KEYTYPE_SOUND_DOWN)
    media_volume_up = KeyCode._from_media(NX_KEYTYPE_SOUND_UP)
    media_previous = KeyCode._from_media(NX_KEYTYPE_PREVIOUS)
    media_next = KeyCode._from_media(NX_KEYTYPE_NEXT)
# pylint: enable=W0212


class Controller(_base.Controller):
    _KeyCode = KeyCode
    _Key = Key

    def __init__(self):
        super(Controller, self).__init__()
        self._mapping = get_unicode_to_keycode_map()

    def _handle(self, key, is_press):
        with self.modifiers as modifiers:
            Quartz.CGEventPost(
                Quartz.kCGHIDEventTap,
                (key if key not in (k for k in Key) else key.value)._event(
                    modifiers, self._mapping, is_press))


class Listener(ListenerMixin, _base.Listener):
    #: The events that we listen to
    _EVENTS = (
        Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown) |
        Quartz.CGEventMaskBit(Quartz.kCGEventKeyUp) |
        Quartz.CGEventMaskBit(Quartz.kCGEventFlagsChanged) |
        Quartz.CGEventMaskBit(Quartz.NSSystemDefined)
    )

    # pylint: disable=W0212
    #: A mapping from keysym to special key
    _SPECIAL_KEYS = {
        (key.value.vk, key.value._is_media): key
        for key in Key}
    # pylint: enable=W0212

    #: The event flags set for the various modifier keys
    _MODIFIER_FLAGS = {
        Key.alt: Quartz.kCGEventFlagMaskAlternate,
        Key.alt_l: Quartz.kCGEventFlagMaskAlternate,
        Key.alt_r: Quartz.kCGEventFlagMaskAlternate,
        Key.cmd: Quartz.kCGEventFlagMaskCommand,
        Key.cmd_l: Quartz.kCGEventFlagMaskCommand,
        Key.cmd_r: Quartz.kCGEventFlagMaskCommand,
        Key.ctrl: Quartz.kCGEventFlagMaskControl,
        Key.ctrl_l: Quartz.kCGEventFlagMaskControl,
        Key.ctrl_r: Quartz.kCGEventFlagMaskControl,
        Key.shift: Quartz.kCGEventFlagMaskShift,
        Key.shift_l: Quartz.kCGEventFlagMaskShift,
        Key.shift_r: Quartz.kCGEventFlagMaskShift,
        Key.fn: Quartz.kCGEventFlagMaskSecondaryFn}

    def __init__(self, *args, **kwargs):
        super(Listener, self).__init__(*args, **kwargs)
        self._flags = 0
        self._context = None
        self._intercept = self._options.get(
            'intercept',
            None)
        self._is_caps_lock_on = False

    def _run(self):
        with keycode_context() as context:
            self._context = context
            try:
                super(Listener, self)._run()
            finally:
                self._context = None

    def _handle(self, _proxy, event_type, event, _refcon):
        '''Returns whether to suppress the event after reporting it.
        '''
        # Convert the event to a KeyCode; this may fail, and in that case we
        # pass None
        try:
            key = self._event_to_key(event)
        except IndexError:
            key = None

        should_suppress = False
        try:
            if event_type == Quartz.kCGEventKeyDown:
                # This is a normal key press
                should_suppress = self.on_press(key) == 2

            elif event_type == Quartz.kCGEventKeyUp:
                # This is a normal key release
                should_suppress = self.on_release(key) == 2

            elif key == Key.caps_lock:
                # Use the current flags and new flags to figure whether it's a press
                if event_type == Quartz.NSEventTypeFlagsChanged:
                    should_suppress = self.on_press(key) == 2
                    self._is_caps_lock_on = Quartz.CGEventGetFlags(event) & 1 << 16 > 0
                else:
                    should_suppress = self.on_release(key) == 2

            elif event_type == Quartz.NSSystemDefined:
                sys_event = Quartz.NSEvent.eventWithCGEvent_(event)
                if sys_event.subtype() == kSystemDefinedEventMediaKeysSubtype:
                    # The key in the special key dict; True since it is a media
                    # key
                    key = ((sys_event.data1() & 0xffff0000) >> 16, True)
                    if key in self._SPECIAL_KEYS:
                        flags = sys_event.data1() & 0x0000ffff
                        is_press = ((flags & 0xff00) >> 8) == 0x0a
                        if is_press:
                            should_suppress = self.on_press(self._SPECIAL_KEYS[key]) == 2
                        else:
                            should_suppress = self.on_release(self._SPECIAL_KEYS[key]) == 2

            else:
                # This is a modifier event---excluding caps lock---for which we
                # must check the current modifier state to determine whether
                # the key was pressed or released
                if key not in self._MODIFIER_FLAGS:
                    return False

                flags = Quartz.CGEventGetFlags(event)
                is_press = flags & self._MODIFIER_FLAGS[key]
                if is_press:
                    should_suppress = self.on_press(key) == 2
                else:
                    should_suppress = self.on_release(key) == 2

                if should_suppress:
                    Quartz.CGEventSetFlags(event, self._flags)
                else:
                    Quartz.CGEventPost(
                        Quartz.kCGHIDEventTap,
                        (key.value)._event(set(), {}, is_press))

            return should_suppress
        finally:
            # Store the current flag mask to be able to detect modifier state
            # changes
            if not should_suppress:
                self._flags = Quartz.CGEventGetFlags(event)

    def _event_to_key(self, event):
        """Converts a *Quartz* event to a :class:`KeyCode`.

        :param event: The event to convert.

        :return: a :class:`pynput.keyboard.KeyCode`

        :raises IndexError: if the key code is invalid
        """
        vk = Quartz.CGEventGetIntegerValueField(
            event, Quartz.kCGKeyboardEventKeycode)
        event_type = Quartz.CGEventGetType(event)
        is_media = True if event_type == Quartz.NSSystemDefined else None

        # First hard-check if it's a caps lock release...
        flags = Quartz.CGEventGetFlags(event)
        old_8 = self._flags & 1 << 8 > 0
        new_8 = flags & 1 << 8 > 0
        old_16 = self._flags & 1 << 16 > 0
        new_16 = flags & 1 << 16 > 0
        if event_type == Quartz.NSEventTypeSystemDefined and not old_8 and new_8 \
                and (old_16 or new_16) and (old_16 == new_16) == self._is_caps_lock_on:
            return Key.caps_lock

        # ...then try other special keys...
        key = (vk, is_media)
        if key in self._SPECIAL_KEYS:
            return self._SPECIAL_KEYS[key]

        # ...then try characters...
        length, chars = Quartz.CGEventKeyboardGetUnicodeString(
            event, 100, None, None)
        try:
            printable = chars.isprintable()
        except AttributeError:
            printable = chars.isalnum()
        if not printable and vk in SYMBOLS \
                and Quartz.CGEventGetFlags(event) \
                & Quartz.kCGEventFlagMaskControl:
            return KeyCode.from_char(SYMBOLS[vk], vk=vk)
        elif length > 0:
            return KeyCode.from_char(chars, vk=vk)

        # ...and fall back on a virtual key code
        return KeyCode.from_vk(vk)

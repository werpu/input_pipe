//go:build darwin

// key_server — TCP keyboard injection server for macOS.
// Uses CGEventCreateKeyboardEvent via CoreGraphics (CGo).
// Requires Accessibility permission: System Preferences → Security & Privacy → Accessibility.
//
// Usage:
//
//	key_server [-p port]   default port 9003
package main

/*
#cgo LDFLAGS: -framework ApplicationServices
#include <ApplicationServices/ApplicationServices.h>

void post_key(CGKeyCode code, int down) {
    CGEventRef e = CGEventCreateKeyboardEvent(NULL, code, (Boolean)(down != 0));
    CGEventPost(kCGHIDEventTap, e);
    CFRelease(e);
}
*/
import "C"

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"net"
	"os"
	"strings"
	"time"
)

const delay = 50 * time.Millisecond

// Linux KEY_* name → macOS CGKeyCode (HIToolbox virtual key codes)
var keyMap = map[string]C.CGKeyCode{
	"KEY_A": 0x00, "KEY_S": 0x01, "KEY_D": 0x02, "KEY_F": 0x03,
	"KEY_H": 0x04, "KEY_G": 0x05, "KEY_Z": 0x06, "KEY_X": 0x07,
	"KEY_C": 0x08, "KEY_V": 0x09, "KEY_B": 0x0B, "KEY_Q": 0x0C,
	"KEY_W": 0x0D, "KEY_E": 0x0E, "KEY_R": 0x0F, "KEY_Y": 0x10,
	"KEY_T": 0x11,
	"KEY_1": 0x12, "KEY_2": 0x13, "KEY_3": 0x14, "KEY_4": 0x15,
	"KEY_6": 0x16, "KEY_5": 0x17, "KEY_9": 0x19, "KEY_7": 0x1A,
	"KEY_8": 0x1C, "KEY_0": 0x1D,
	"KEY_O": 0x1F, "KEY_U": 0x20, "KEY_I": 0x22, "KEY_P": 0x23,
	"KEY_ENTER":     0x24,
	"KEY_L": 0x25, "KEY_J": 0x26, "KEY_K": 0x28,
	"KEY_N": 0x2D, "KEY_M": 0x2E,
	"KEY_TAB":        0x30,
	"KEY_SPACE":      0x31,
	"KEY_BACKSPACE":  0x33,
	"KEY_ESC":        0x35,
	"KEY_LEFTMETA":   0x37,
	"KEY_LEFTSHIFT":  0x38,
	"KEY_CAPSLOCK":   0x39,
	"KEY_LEFTALT":    0x3A,
	"KEY_LEFTCTRL":   0x3B,
	"KEY_RIGHTSHIFT": 0x3C,
	"KEY_RIGHTALT":   0x3D,
	"KEY_RIGHTCTRL":  0x3E,
	"KEY_RIGHTMETA":  0x37,
	"KEY_DELETE":     0x75,
	"KEY_HOME":       0x73,
	"KEY_END":        0x77,
	"KEY_PAGEUP":     0x74,
	"KEY_PAGEDOWN":   0x79,
	"KEY_LEFT":       0x7B,
	"KEY_RIGHT":      0x7C,
	"KEY_DOWN":       0x7D,
	"KEY_UP":         0x7E,
	"KEY_F1":  0x7A, "KEY_F2":  0x78, "KEY_F3":  0x63, "KEY_F4":  0x76,
	"KEY_F5":  0x60, "KEY_F6":  0x61, "KEY_F7":  0x62, "KEY_F8":  0x64,
	"KEY_F9":  0x65, "KEY_F10": 0x6D, "KEY_F11": 0x67, "KEY_F12": 0x6F,
	"KEY_KPENTER":    0x4C,
	"KEY_KPPLUS":     0x45,
	"KEY_KPMINUS":    0x4E,
	"KEY_KPASTERISK": 0x43,
	"KEY_KPDOT":      0x41,
	"KEY_KP0": 0x52, "KEY_KP1": 0x53, "KEY_KP2": 0x54, "KEY_KP3": 0x55,
	"KEY_KP4": 0x56, "KEY_KP5": 0x57, "KEY_KP6": 0x58, "KEY_KP7": 0x59,
	"KEY_KP8": 0x5B, "KEY_KP9": 0x5C,
}

type message struct {
	To    string `json:"to"`
	Event string `json:"event"`
	Long  string `json:"long"`
}

// parseEvent returns the KEY_* name and explicit value (-1 if absent).
func parseEvent(ev string) (keyName string, value int) {
	value = -1
	parts := strings.SplitN(ev, ",", 3)
	if len(parts) < 2 {
		return
	}
	f := strings.Fields(strings.TrimSpace(parts[1]))
	if len(f) >= 3 {
		keyName = strings.Trim(f[2], "()")
	}
	if len(parts) >= 3 {
		vf := strings.Fields(strings.TrimSpace(parts[2]))
		if len(vf) >= 2 && vf[0] == "value" {
			fmt.Sscanf(vf[1], "%d", &value)
		}
	}
	return
}

func pressKey(code C.CGKeyCode, value int, long bool) {
	switch value {
	case 1:
		C.post_key(code, 1)
		if long {
			for i := 0; i < 10; i++ {
				time.Sleep(delay)
				C.post_key(code, 1)
			}
		}
	case 0:
		C.post_key(code, 0)
	case 2:
		C.post_key(code, 1)
	default:
		// legacy: no value → full press+release
		C.post_key(code, 1)
		if long {
			for i := 0; i < 10; i++ {
				time.Sleep(delay)
				C.post_key(code, 1)
			}
		}
		time.Sleep(delay)
		C.post_key(code, 0)
	}
}

func handleConn(conn net.Conn) {
	defer conn.Close()
	scanner := bufio.NewScanner(conn)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" {
			continue
		}
		if strings.HasPrefix(line, "trigger_input ") {
			line = line[len("trigger_input "):]
		}
		var m message
		if err := json.Unmarshal([]byte(line), &m); err != nil {
			fmt.Fprintf(os.Stderr, "parse error: %v\n", err)
			continue
		}
		keyName, value := parseEvent(m.Event)
		code, ok := keyMap[keyName]
		if !ok {
			fmt.Fprintf(os.Stderr, "unknown key: %s\n", keyName)
			continue
		}
		pressKey(code, value, strings.ToLower(m.Long) == "true")
	}
}

func main() {
	port := flag.Int("p", 9003, "port to listen on")
	flag.Parse()

	ln, err := net.Listen("tcp4", fmt.Sprintf("0.0.0.0:%d", *port))
	if err != nil {
		fmt.Fprintf(os.Stderr, "listen: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("listening on port %d\n", *port)
	for {
		conn, err := ln.Accept()
		if err != nil {
			fmt.Fprintf(os.Stderr, "accept: %v\n", err)
			continue
		}
		go handleConn(conn)
	}
}

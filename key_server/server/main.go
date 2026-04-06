//go:build linux

// key_server — TCP keyboard injection server for Linux.
// Creates a virtual keyboard via uinput and injects keystrokes.
//
// Requires write access to /dev/uinput:
//
//	SUBSYSTEM=="misc", KERNEL=="uinput", MODE="0660", GROUP="input"
//
// Usage:
//
//	key_server [-p port]   default port 9003
package main

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"net"
	"os"
	"strings"
	"time"

	"github.com/bendahl/uinput"
)

const delay = 50 * time.Millisecond

// Linux key codes: KEY_* name → uinput key code (= Linux input event code)
var keyMap = map[string]int{
	"KEY_ESC":        1,
	"KEY_1": 2, "KEY_2": 3, "KEY_3": 4, "KEY_4": 5, "KEY_5": 6,
	"KEY_6": 7, "KEY_7": 8, "KEY_8": 9, "KEY_9": 10, "KEY_0": 11,
	"KEY_MINUS": 12, "KEY_EQUAL": 13,
	"KEY_BACKSPACE": 14,
	"KEY_TAB":       15,
	"KEY_Q": 16, "KEY_W": 17, "KEY_E": 18, "KEY_R": 19, "KEY_T": 20,
	"KEY_Y": 21, "KEY_U": 22, "KEY_I": 23, "KEY_O": 24, "KEY_P": 25,
	"KEY_ENTER":    28,
	"KEY_LEFTCTRL": 29,
	"KEY_A": 30, "KEY_S": 31, "KEY_D": 32, "KEY_F": 33, "KEY_G": 34,
	"KEY_H": 35, "KEY_J": 36, "KEY_K": 37, "KEY_L": 38,
	"KEY_SEMICOLON": 39,
	"KEY_LEFTSHIFT": 42,
	"KEY_Z": 44, "KEY_X": 45, "KEY_C": 46, "KEY_V": 47, "KEY_B": 48,
	"KEY_N": 49, "KEY_M": 50,
	"KEY_COMMA": 51, "KEY_DOT": 52, "KEY_SLASH": 53,
	"KEY_RIGHTSHIFT":  54,
	"KEY_KPASTERISK":  55,
	"KEY_LEFTALT":     56,
	"KEY_SPACE":       57,
	"KEY_CAPSLOCK":    58,
	"KEY_F1":  59, "KEY_F2":  60, "KEY_F3":  61, "KEY_F4":  62,
	"KEY_F5":  63, "KEY_F6":  64, "KEY_F7":  65, "KEY_F8":  66,
	"KEY_F9":  67, "KEY_F10": 68,
	"KEY_F11": 87, "KEY_F12": 88,
	"KEY_RIGHTCTRL": 97,
	"KEY_RIGHTALT":  100,
	"KEY_HOME":      102,
	"KEY_UP":        103,
	"KEY_PAGEUP":    104,
	"KEY_LEFT":      105,
	"KEY_RIGHT":     106,
	"KEY_END":       107,
	"KEY_DOWN":      108,
	"KEY_PAGEDOWN":  109,
	"KEY_DELETE":    111,
	"KEY_LEFTMETA":  125,
	"KEY_RIGHTMETA": 126,
	"KEY_KP7": 71, "KEY_KP8": 72, "KEY_KP9": 73,
	"KEY_KPMINUS": 74,
	"KEY_KP4": 75, "KEY_KP5": 76, "KEY_KP6": 77,
	"KEY_KPPLUS": 78,
	"KEY_KP1": 79, "KEY_KP2": 80, "KEY_KP3": 81,
	"KEY_KP0": 82, "KEY_KPDOT": 83,
	"KEY_KPENTER": 96,
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

func pressKey(kb uinput.Keyboard, code int, value int, long bool) error {
	switch value {
	case 1:
		if err := kb.KeyDown(code); err != nil {
			return err
		}
		if long {
			for i := 0; i < 10; i++ {
				time.Sleep(delay)
				if err := kb.KeyDown(code); err != nil {
					return err
				}
			}
		}
	case 0:
		return kb.KeyUp(code)
	case 2:
		return kb.KeyDown(code)
	default:
		// legacy: no value → full press+release
		if err := kb.KeyDown(code); err != nil {
			return err
		}
		if long {
			for i := 0; i < 10; i++ {
				time.Sleep(delay)
				if err := kb.KeyDown(code); err != nil {
					return err
				}
			}
		}
		time.Sleep(delay)
		return kb.KeyUp(code)
	}
	return nil
}

func handleConn(conn net.Conn, kb uinput.Keyboard) {
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
		if err := pressKey(kb, code, value, strings.ToLower(m.Long) == "true"); err != nil {
			fmt.Fprintf(os.Stderr, "key error: %v\n", err)
		}
	}
}

func main() {
	port := flag.Int("p", 9003, "port to listen on")
	flag.Parse()

	kb, err := uinput.CreateKeyboard("/dev/uinput", []byte("key-server-kbd"))
	if err != nil {
		fmt.Fprintf(os.Stderr, "uinput: %v\n", err)
		os.Exit(1)
	}
	defer kb.Close()

	ln, err := net.Listen("tcp", fmt.Sprintf(":%d", *port))
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
		go handleConn(conn, kb)
	}
}

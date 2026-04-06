// key_client — send one or more keystrokes to key_server over a single connection.
//
// Full input_pipe trigger_input protocol. Each keystroke sends value 1 (down)
// followed by value 0 (up). Append :long to simulate a held key.
//
// Usage:
//
//	key_client <host> <port> <event>[;<event>...] [--to TARGET]
//
// Examples:
//
//	key_client localhost 9003 "(EV_KEY), code 28 (KEY_ENTER)"
//	key_client localhost 9003 "(EV_KEY), code 28 (KEY_ENTER):long"
//	key_client localhost 9003 "(EV_KEY), code 35 (KEY_H);(EV_KEY), code 18 (KEY_E);(EV_KEY), code 28 (KEY_ENTER)"
//	key_client localhost 9003 "(EV_KEY), code 28 (KEY_ENTER)" --to keybd1
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"net"
	"os"
	"strings"
)

type message struct {
	To    string `json:"to"`
	Event string `json:"event"`
	Long  string `json:"long"`
}

type keyEvent struct {
	base string
	long bool
}

func parseEvents(raw string) []keyEvent {
	var out []keyEvent
	for _, part := range strings.Split(raw, ";") {
		part = strings.TrimSpace(part)
		if part == "" {
			continue
		}
		if strings.HasSuffix(part, ":long") {
			out = append(out, keyEvent{strings.TrimSpace(part[:len(part)-5]), true})
		} else {
			out = append(out, keyEvent{part, false})
		}
	}
	return out
}

func makePayload(to string, events []keyEvent) []byte {
	var sb strings.Builder
	for _, ev := range events {
		longStr := "false"
		if ev.long {
			longStr = "true"
		}
		for _, msg := range []message{
			{To: to, Event: ev.base + ", value 1", Long: longStr},
			{To: to, Event: ev.base + ", value 0", Long: "false"},
		} {
			b, _ := json.Marshal(msg)
			sb.WriteString("trigger_input ")
			sb.Write(b)
			sb.WriteByte('\n')
		}
	}
	return []byte(sb.String())
}

func main() {
	to := flag.String("to", "keybd1", "target device name")
	flag.Parse()

	args := flag.Args()
	if len(args) < 3 {
		fmt.Fprintln(os.Stderr, "usage: key_client <host> <port> <event>[;<event>...] [--to TARGET]")
		os.Exit(1)
	}

	host, port, raw := args[0], args[1], args[2]

	conn, err := net.Dial("tcp", host+":"+port)
	if err != nil {
		fmt.Fprintf(os.Stderr, "connect: %v\n", err)
		os.Exit(1)
	}
	defer conn.Close()

	if _, err = conn.Write(makePayload(*to, parseEvents(raw))); err != nil {
		fmt.Fprintf(os.Stderr, "send: %v\n", err)
		os.Exit(1)
	}
}

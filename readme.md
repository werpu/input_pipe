# Input Pipe

## What is this?

To make it simple, it was developed as universal joystick mapper 
for my personal usecase.
The idea was to have a simple piple which can map multiple inputs
into multiple outputs and provide basic device emulation for the
outputs.

## Are there alternative solutions

Yes there are, but they either provided to lack the m:n capabilities 
(most either map from joystick to keyboard), or they 
were buggy and EOL. Believe me, I spent several months
trying to navigate around bugs trying to fix issues before
I started my own mapper.

## Goals

The goals were simple.
* Easy: to maintain, this is achieved by using a high level language

* Fast: given that Python is not the fastest language I had
to chose the internal data structures carefully

* Easily extensible, this was achieved by providing a basic device api

* Easily configurable: by using YAML this was easily achieved, but
the config files are a little bit verbose, theoretically I could carefully
strip down the number of lines per config by adding artificial language
constructs, but you usually program the config once and then
almost never touch it again, so I can live with what I have for now.
The configuration has not too many config elements and they should be easy to grasp.

* Real m:n mapping no questions asked: I basically can map from any input
to any output, given the output type is supported by an underlying 
easy to program driver. Drivers for mouse, keyboard and an XBOX 360 controller
type are supported. Others may be added in the furure or can be provided
by someone who has the need for it (hey this is opensource so feel 
free to participate)

## Does it work?

Yes as the time of writing I have it working but no final version yet
so smaller adjustments still might be needed on my side.

## Automated setup?

Not yet, setup instructions will be provided below.

## Any other version than something for linux?

Not yet planned, this program relies heavily on the linux evdev/input mechanisms, and
frankly spoken I need it for linux only for the time being.
If someone wants to do a windows version, feel free to 
fork the code and replace all the evdev bindings with DirectInput or
SDL bindings.

## Instructions

### General instructions

The mapper relies on a single configuration file provided by the user
which is broken into several sections.

1. The input configuration section

This section defines the input devices and how to find then

2. The output configuration Section

A general definition of which output devices of which type to generate

3. The rule section

Defines on what needs to happen from an input event onwards
aka key A pressed -> rule match -> button X on virtual joystick 1 is triggered


All of those rules are atm combined into one single big YAML file,
you can find examples for those configurations in src/test/resources
and src/main/resources

#### The input device section


The input device section lays out which input devices to touch and to fetch
the events from.
A classical input device secion looks like this

```yaml
inputs:

  digital:
    name: Ultimarc I-PAC Ultimarc I-PAC
    exclusive: true
    relpos: 1

  analog_left:
    name_re: ^Ultimarc.*Ultrastik\sPlayer\ 1$
    exclusive: true
    relpos: 1

  analog_right:
    name_re: ^Ultimarc.*Ultrastik\sPlayer\ 2$
    exclusive: true
    relpos: 1
```

Now what happens here?
We have three input devices which we have to react upon.
Have a look at the first one:

```yaml
inputs:

  digital:
    name: Ultimarc I-PAC Ultimarc I-PAC
    exclusive: true
    relpos: 1
```


* **inputs** defines this section as input device definition section
* **digital** is the internal key to the newly defined input device
* The next part under **digital** describes the general pattern of the device
    * **name** defines an exact match for the name of the device

    * **exclusive** if set to true the device is locked and cannot be taken from any other program (useful if a program 
        relies on input auto detection). This means the input events emitted by this device
        will be used only by the mapper and no other program (default value is false)

    * **relpos** sometimes there are several devices which match, the relpos defines
        which of those devices should be taken for the input events (the order is by the order
        in the /dev/input/event nodes, aka input0 comes before input 10 etc...). 
        One note, the exclusive will lock all the matches not only the input source.
        So choose your matches wisely, if you do not want them. There are other ways to achieve a match, which we will see in the next example.

```yaml
    analog_left:
      name_re: ^Ultimarc.*Ultra\-Stik\sPlayer\ 1$
      exclusive: true
      relpos: 1
```

So what happens here? Basically the same as before,
but with the exception of doing a regular expression match
instead of a full name match.

We have following match possibilities atm:

* **name** name match
* **name_re** name regular expression match
* **phys** match for a phys address as given by **lsinput**
* **phys_re** regular expression match for phys

So what happens if I combine several of those? 

Easy, if you for instance provide name and phys then both
criteria must match.

You cannot provide two name at the same time on the same device
however.

#### The Output Device Section
Every pipe has two ends, right?
In our case definitely. The definition of the output
devices is the second end of the pipe.
The output device section tells which devces the signals should 
go to. Those are artificial devices mimicking different 
device types.
At the time of writing following output device types are supported

* xbox 360 controller
* mouse
* keyboard

Practically it is possible to provide additional device
types by implementing a small driver (TODO add documentation).

So how does an output section look like?

```yaml
outputs:

  xbox1:
    name: Microsoft X-Box 360 pad
    type: xbx360

  xbox2:
    name: Microsoft X-Box 360 pad
    type: xbx360

  mouse1:
    name: mouse
    type: mouse

  keybd1:
    name: key1
    type: keybd
```

The output definitions are rather simple,
under outputs you define an output device
by its internal key (xbox1 or keybd1) for instance.
The next subsections are the device name exposed
to linux and the type.

Currently following types are possible:
* xbx360 ... which generates a virtual xbox 360 controller
* mouse ... which generates a virtual mouse to map events into mouse movements and events
* keybd ... a virtual keyboard which lets you expose simulated keystrokes

If you want to program your own driver, the drivers
can be found in src/main/python/drivers

### The Rules Section

What would be a pipe without rules on how to map
the incoming inputs to the outgoing outputs?

And last but not least we are going to define those rules
in the rules section.

A rule would look like following

```yaml
  - from: digital
    target_rules:
      - from_ev: (EV_KEY), code 103 (KEY_UP)     # keyup event as coming in from evtest
        targets:
          - to: xbox1                            # artificial xbox controiler
            to_ev: (EV_ABS), code 17 (ABS_HAT0Y), value -1   # pad up event

      - from_ev: (EV_KEY), code 108 (KEY_DOWN)   # keyup event as coming in from evtest
        targets:
          - to: xbox1
            to_ev: (EV_ABS), code 17 (ABS_HAT0Y), value 1   # pad down event

```

The structure of rules are very simple.
You basically define a from section which tells you
on which input device you listen to. 
Then on each input device you define a set of target rules
which basically consist of following parts

* from_ev:  the incoming event definition (the same pattern you will see if you use **evtest**)
* targets: a set of possible output targets
    * to: the output device ("internal device key as defined by the outputs section")
    * to_ev: the event as it would be seen by evtest
        note the main difference to evtest is that the value part is optional
        you will need it only if you want to expose a different value than what is provided from the input (aka -1 instead of 1)
 
##### How Do I get the Device Names and Event Codes

This is rather straight forward.
lsinput will give you an overview of your input devices
evtest will allow you to fetch the exposed events.
 
 
##### Special Cases

###### One Input Event Multiple Events to Different Targets

```yaml
  - from: analog_right
    target_rules:
      - from_ev: (EV_ABS), code 1 (ABS_Y)  # up down
        targets:
          - to: xbox1
            to_ev: (EV_ABS), code 4 (ABS_RY)
          - to: xbox2
            to_ev: (EV_ABS), code 1 (ABS_Y)
``
This example maps two analog events from analog_right
to the controllers xbox one right stick
and xbox2 left stick

###### Mapping of Values

``ỳaml
- from: digital
    target_rules:
      - from_ev: (EV_KEY), code 103 (KEY_UP)     # keyup event as coming in from evtest
        targets:
          - to: xbox1                            # artificial xbox controiler
            to_ev: (EV_ABS), code 17 (ABS_HAT0Y), value -1   # pad up event
``
        
This maps the button with the code 103 to a d-pad button press.
The speciality of this event is that whenever the input event
is coming in with a value of 1 (button pressed)
it automatically is converted to -1 which is the 
value the d-pad would expose on the xbox one controller.




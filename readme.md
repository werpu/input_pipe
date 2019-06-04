# Inputm Pipe

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

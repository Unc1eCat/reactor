# **Reactor**
*Python event signaling framework*

-----------------

## Overview

Reactor is a Python framework that provides some asynchronous and events signaling tools. The heart of the framework is the reactor singleton (subclasses of `AbstractReactor`). Create an instance of the singleton and keep it safe somewhere where anything will be able to reach out to it.    

The main principle and slogan of the framework is:

    Everyone knows everything 

A reactor can contain components. Each component defines a "on_event" method. Whenever an event is emitted to the reactor, the reactor passes the event to each "on_event" method of each of its components. This is how the principle is fulfilled.

## Development Progress

The creation of the framework isn't finished yet. It can be said to be in alpha stage. 


# **Reactor**
*Python event signaling and dependency injection framework*

-----------------

## Overview
Reactor is a Python framework that provides some asynchronous and events signaling tools. The heart of the framework is the reactor singleton (subclasses of `AbstractReactor`). Create an instance of the singleton and keep it safe somewhere where anything will be able to reach out to it.    

The main principle and slogan of the framework is:

    Everyone knows everything 



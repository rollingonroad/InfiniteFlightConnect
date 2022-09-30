# Infinite Flight Connect API Client

Using python to connect the Infinite Flight Connect API v1/v2.

## Installation

```sh
pip3 install ifcclient
```

## Usage

Before getting started, make sure to enable the Infinite Flight Coneect in the app `Settings > General > Enable Infinite Flight Connect`

First, import the module in Python and init the object.
```py
import ifcclient

ifc = ifcclient.IFClient()
```

There are three ways to use the Infinite Flight Connected API V2, GetState, SetState, RunCommand. 

###GetState
```py
ifc.get_state_by_name(name)
```

###SetState
```py
ifc.set_state_by_name(name, value)
```

###RunCommand
```py
ifc.run_command_by_name(command)
```

## Future updates

- [ ] To support Connect API v1
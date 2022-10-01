# Infinite Flight Connect API Client

Using python to connect the Infinite Flight Connect API v1/v2.

## Installation

```sh
pip3 install ifcclient
```

## Usage

Before getting started, make sure to enable the Infinite Flight Coneect in the app `Settings > General > Enable Infinite Flight Connect`

First, import the module in Python and discover devcies in the same network, you can use duration to specific the time to discover, you can use duration=0 to return the first device you discovered.
```py
import ifcclient
devices = IFCClient.discover_devices(duration=0)
```

### API V2
Init the client object.
```py
ifc = ifcclient.IFClient(devices[0], version=2) # version is 2 by default
```
There are three ways to use the Infinite Flight Connected API V2, GetState, SetState, RunCommand. You can check Infinite Flight website for the detail of API.

#### GetState
```py
ifc.get_state_by_name(name)
# For example
ifc.get_state_by_name('aircraft/0/systems/flaps/state')
```

#### SetState
```py
ifc.set_state_by_name(name, value)
# For example
ifc.set_state_by_name('aircraft/0/systems/flaps/state', 2)
```

#### RunCommand
```py
ifc.run_command_by_name(command)
# For example
ifc.run_command_by_name('commands/NextCamera')
```

### API V1
Init the client object for V1.
```py
ifc = ifcclient.IFClient(devices[0], version=1)
```
For V1, to send a command, use the `send_command` function. The first parameter is the command, the second parameter are the parameters passed to Infinite Flight while the third parameter determines whether to wait for a response or not. Await response is false by default although it must be enabled when expecting a response.
```py

ifc.send_command("{CommandName}", [Parameters], await_response=True)
ifc.send_command("{CommandName}", [Parameters]) # await_response is False by default
# For example
ifc.send_command("airplane.getstate", [], await_response=True)
ifc.send_command("flightplan.get", [], await_response=True)
```

## Future updates

- [ ] 
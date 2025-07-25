# Spacewidget

⚠️ This repository is archived. In our internal repo is spacewidget2.

A widget to display how many people are present.

## Relay

Run the relay somewhere where it can access your mqtt. It will connect to the widget and send updates via websockets.

### Configuration

These environment variables are availible:

* `WS_URL`: The url where the widget runs.
* `TOKEN`: Security token to authenticate against the widget.
* `MQTT_URL`: The url of the mqtt server.
* `TOPICS`: A comma seperated list of mqtt topics that shall be pushed through the websocket.

## Widget

The widget should run somewhere on the internet. It needs to be accessed by the Relay and your visitors.

### Configuration

These environment variables are availible:

* `WS_TOKEN`: Security token that is required to update, needs to be the same as relay uses.
* `METRICS_TOKEN`: Token for the HTTP header to acces `/metrics`.
* `MEMBER_TOPIC`: Name of the topic that will be displayed in the widget.
* `LISTEN`: A socket (`unix:///var/run/widget.sock`) or a address (`localhost:8080`) to listen on.

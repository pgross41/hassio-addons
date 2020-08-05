# dvr163-hass
Home Assistant Add-on for interacting with Eseenet/dvr163 NVR

This add-on is a single container that runs 2 services: 

* Postfix SMTP server (port 25)
* Python web server (port 8080)

The Python server is the main entrypoint process and contains all the logic, Postfix is used as a vehicle to receive emails and provide them to Python. The postfix server runs in the background (but will output to the regular Docker logs). When it receives an email it will POST the contents to the `/api/email` endpoint of the Python web server. 

## Development

Open the project directory in VS Code and accept when prompted to open in dev container. This will open the project in a container that contains an instance of Home Assistant. Run the `hass-run` task to start Home Assistant, once running it is accessible at http://localhost:8123. Navigate to the Supervisor tab and install the `Eseenet/dvr163 NVR` add-on. From there you can make changes and click "Rebuild" from Home Assistant and the changes will be applied and can be tested live. 

### Debugging

There are launch configs for running the Python scripts in the container in VS Code with debug support. This technically does not require Home Assistant to be running but it is suggested to run the `hass-run` task because it starts Docker in the devcontainer which is needed to debug Python. There are 2 launch configs: 

1. Flask - Runs the main web server just like the full add-on (but without the Postfix SMTP server)
1. handle_email.py - Directly runs the email handler script with a test email

An `options.json` file with runtime configuration must be provided. When debugging it will look in `/app/dev/env/options.json`, otherwise it uses Home Assistant's default `/data/options.json` location. 

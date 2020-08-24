# Home Assistant Add-on: Eseenet/dvr163 NVR

Accept "motion detection" emails from an Eseenet/dvr163 NVR and execute configurable actions with the data. 

## NVR Configuration

The NVR must send the emails to Home Assistan. From the main system menu go to `Network Setup` > `E-Mail` and use the following configuration. The `hass` user is required, replace only the `SMTP Server` with the address of your home assistant: 

![image](https://user-images.githubusercontent.com/11710621/91005315-2c5a5d80-e59c-11ea-883c-3767ae463925.png)

That will send motion detection events to the add-on. 

## Supported actions: 

### Dropbox
Upload the image to Dropbox. When creating an access token it is suggested to create an "app" in Dropbox with access only limited to the app folder. Images are saved with the following folder/naming convention: 
```
ch<channel number>/<date>/<time>.jpg
```
The date and time do not use system time, it uses whatever timestamp text is in the body of the email. This makes it easy to find the relevant video later since the time is synced with the NVR and is not impacted by network latency. 

### Email
Forward the email to another email address (only tested with Gmail). This is to maintain backwards compatability since the NVR is no longer sending emails to a true inbox. It also allows you to completely block the NVR from accessing the internet if desired e.g. at the router level. 

## How it works

The add-on is a single container that runs 2 services: 

* Postfix SMTP server (port 25)
* Python web server (port 8080)

The Python server is the main entrypoint process and contains all the logic, Postfix is used as a vehicle to receive emails and provide them to Python. The postfix server runs in the background. When it receives an email it will POST the contents to the `/api/email` endpoint of the Python web server. 

## Development

Open the project directory in VS Code and accept when prompted to open in dev container. This will open the project in a container that contains an instance of Home Assistant. Run the `hass-run` task to start Home Assistant, once running it is accessible at http://localhost:8123. Navigate to the Supervisor tab and install the `Eseenet/dvr163 NVR` add-on. From there you can make changes and click "Rebuild" from Home Assistant and the changes will be applied and can be tested live. 

### Debugging

There are launch configs for running the Python scripts in the container in VS Code with debug support. This technically does not require Home Assistant to be running but it is suggested to run the `hass-run` task because it starts Docker in the devcontainer which is needed to debug Python. There are 2 launch configs: 

1. Flask - Runs the main web server just like the full add-on (but without the Postfix SMTP server)
1. handle_email.py - Directly runs the email handler script with a test email

An `options.json` file with runtime configuration must be provided. When debugging it will look in `/app/dev/env/options.json`, otherwise it uses Home Assistant's default `/data/options.json` location. 

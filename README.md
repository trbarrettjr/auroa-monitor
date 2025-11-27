# App description

This is a simple app that will monitor the Space Weather Prediction Center's data on the Planetary K-index.

I have this to notify me when the Kp index is greater than or equal to 5 and it has not sent me the same message.

I have the notifications sent through pushover.

## Recommendations

Build the app in the docker file.

I use docker's volumes to persist data.

Then run the following CLI

```bash
docker run --rm -v aurora:/app -e PO_APP_KEY=[PUSHOVER APP KEY] -e PO_USER_KEY=[PUSHOVER USER KEY] aurora:latest
```

I have this setup on the host cron to run on the following:

```crontab
4,24,44 13-23 * * * /usr/bin/docker run --rm -v aurora:/app -e PO_APP_KEY=[PUSHOVER APP KEY] -e PO_USER_KEY=[PUSHOVER USER KEY] aurora:latest
```

This will run at off minutes, hopefully when there is less traffic and I only want to be notified during the selected window.

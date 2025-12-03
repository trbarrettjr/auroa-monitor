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

## Some thoughts...

I keep having these fallacy issues in my head about the math.  Let me explain...

At first, I stored the last 10 observations, I ran a linear regression to see if it was increasing or decreasing.

Then, I thought, why not just grab all the data and run a linear regression on that.

Here is where I see the fallacy...  It is an index that is always changing.  I don't think linear regression is going to do much, especially if the regression has data such as:
| values |
|-------:|
| 5.1    |
| 4.9    |
| 5.0    |
| 5.2    |
| 4.8    |
| 5.0    |
| 5.1    |
| 5.0    |
| 4.9    |
| 5.0    |
| 5.2    |
| 5.0    |
| 4.9    |
| 5.1    |
| 5.0    |
| 5.0    |
| 5.1    |
| 4.9    |
| 5.0    |

This data's linear regression is 0; standard deviation of 0.104853002, and an average of 5.010526316.

If you use it, I would be cautious as to not fall in some statistical fallacy.  I am strongly considering to remove the regression calculations.  I wanted to know what it was trending, but using 40 minutes of data in the data window...

**Update**

I removed the trendline analysis.  See my explanation above.

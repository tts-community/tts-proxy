# tts-proxy

A simple server for forwarding/proxying Tabletop Simulator web requests into standard HTTP.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

# Why?

At present, Tabletop Simulator's `WebRequest` API is _extremely_ limited and doesn't let you read or write headers, and in the case of `POST`s doesn't even let you set the request _body_.

Basically, this means that by default TTS is completely unable to consume the vast majority of third-party web APIs - in particular RESTful APIs are impossible to use _directly_ with TTS' `WebRequest`.

This is where __tts-proxy__ comes in. Instead of communicating with an API directly, __tts-proxy__ acts as an "translator" which takes a TTS web request, and creates a standard HTTP request on your behalf. When the response comes back, __tts-proxy__ does the opposite, converting a standard HTTP response into something you can read inside Tabletop Simulator.

# How do I use this?

As much as it'd be nice to have one pre-setup all TTS mods could share, if we all start using it the traffic could become too significant and it'd either get very slow, or become very expensive to maintain (throwing more resources at it).

So, to alleviate this issue, the idea is that each mod (or each mod developer) would have their own tts-proxy instance running on Heroku. Heroku have a free tier that should be more than enough for any one TTS mod; so there's no cost involved.

The only hiccup is that you need some way of deploying your own copy of tts-proxy. Lucky for you, that big purple "Deploy" button at the top of this page will completely automate the process for you. Yay!

*__NOTE__: You will need a Heroku account, but these are free and __do not__ require credit card details.*

# Security

Anyone hosting your mod will need to be able to communicate with tts-proxy. However, you probably don't want _other mods_ (or random applications) using your proxy!

To _mitigate_ this, we allow you restrict which URLs your tts-proxy deployment is capable of communicating with. If you restrict tts-proxy to communicate with services/URLs that are specific to your mod, then your deployment can't be abused by third-parties trying to use your proxy for other purposes.

We keep it simple and provide just one option (environment variable) you need to set, called `URL_REGEX`. You can update `URL_REGEX` from https://dashboard.heroku.com/apps/<YOUR_HEROKU_DEPLOYMENT_NAME>/settings.

__IMPORTANT__: By default `URL_REGEX` has the value `.+` which means _any_ URL i.e. By default tts-proxy is _not_ restricted._**

As an example, if you wanted to use [Firebase Cloud Firestore](https://firebase.google.com/products/firestore/) as a datastore for your mod, you could restrict `tts-proxy` to communicating with just _your_ Firestore database with:

```
URL_REGEX=https://firestore\.googleapis\.com/v1beta1/projects/<YOUR_PROJECT_ID>/.+
```

This is called a regular expression, specifically it's using [Python regular expression syntax](https://docs.python.org/2/library/re.html).

*__Note:__ You may be wondering why we just don't offer password protection, or encryption. For that to work you'd need to distribute the secret as part of your TTS workshop mod. Meaning to obtain your "secret", all someone would need to do is go looking through your mod!*

# Manual Deployment

If for some reason you don't want to deploy automatically (using the "Deploy" button at the top of the page) you can also deploy manually by following the following procedure.

1. Clone tts-proxy:

    ```bash
    git clone https://github.com/Benjamin-Dobell/tts-proxy.git
    ```

2. Create a Heroku app:

    ```bash
    heroku create
    ```

3. Deploy tts-proxy to your Heroku app:

    ```bash
    git push heroku master
    ```

4. Run the setup script and ensure one dyno is running:

    ```bash
    heroku run ./setup.py
    heroku ps:scale web=1
    ```

    `setup.py` will perform one-time app setup e.g. creating the database.

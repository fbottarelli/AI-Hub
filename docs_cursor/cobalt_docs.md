Directory structure:
└── docs/
    ├── api.md
    ├── configure-for-youtube.md
    ├── protect-an-instance.md
    ├── run-an-instance.md
    ├── examples/
    │   ├── cookies.example.json
    │   └── docker-compose.example.yml
    └── images/
        └── protect-an-instance/


Files Content:

================================================
File: docs/api.md
================================================
# cobalt api documentation
this document provides info about methods and acceptable variables for all cobalt api requests.

> [!IMPORTANT]
> hosted api instances (such as `api.cobalt.tools`) use bot protection and are **not** intended to be used in other projects without explicit permission. if you want to access the cobalt api reliably, you should [host your own instance](/docs/run-an-instance.md) or ask an instance owner for access.

## authentication
an api instance may be configured to require you to authenticate yourself.
if this is the case, you will typically receive an [error response](#error-response)
with a **`api.auth.<method>.missing`** code, which tells you that a particular method
of authentication is required.

authentication is done by passing the `Authorization` header, containing
the authentication scheme and the token:
```
Authorization: <scheme> <token>
```

currently, cobalt supports two ways of authentication. an instance can
choose to configure both, or neither:
- [`Api-Key`](#api-key-authentication)
- [`Bearer`](#bearer-authentication)

### api-key authentication
the api key authentication is the most straightforward. the instance owner
will assign you an api key which you can then use to authenticate like so:
```
Authorization: Api-Key aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
```

if you are an instance owner and wish to configure api key authentication,
see the [instance](run-an-instance.md#api-key-file-format) documentation!

### bearer authentication
the cobalt server may be configured to issue JWT bearers, which are short-lived
tokens intended for use by regular users (e.g. after passing a challenge).
currently, cobalt can issue tokens for successfully solved [turnstile](run-an-instance.md#list-of-all-environment-variables)
challenge, if the instance has turnstile configured. the resulting token is passed like so:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## POST: `/`
cobalt's main processing endpoint.

request body type: `application/json`
response body type: `application/json`

> [!IMPORTANT]
> you must include `Accept` and `Content-Type` headers with every `POST /` request.

```
Accept: application/json
Content-Type: application/json
```

### request body
| key                          | type      | expected value(s)                  | default   | description                                                                     |
|:-----------------------------|:----------|:-----------------------------------|:----------|:--------------------------------------------------------------------------------|
| `url`                        | `string`  | URL to download                    | --        | **must** be included in every request.                                          |
| `videoQuality`               | `string`  | `144 / ... / 2160 / 4320 / max`    | `1080`    | `720` quality is recommended for phones.                                        |
| `audioFormat`                | `string`  | `best / mp3 / ogg / wav / opus`    | `mp3`     |                                                                                 |
| `audioBitrate`               | `string`  | `320 / 256 / 128 / 96 / 64 / 8`    | `128`     | specifies the bitrate to use for the audio. applies only to audio conversion.   |
| `filenameStyle`              | `string`  | `classic / pretty / basic / nerdy` | `classic` | changes the way files are named. previews can be seen in the web app.           |
| `downloadMode`               | `string`  | `auto / audio / mute`              | `auto`    | `audio` downloads only the audio, `mute` skips the audio track in videos.       |
| `youtubeVideoCodec`          | `string`  | `h264 / av1 / vp9`                 | `h264`    | `h264` is recommended for phones.                                               |
| `youtubeDubLang`             | `string`  | `en / ru / cs / ja / es-US / ...`  | --        | specifies the language of audio to download when a youtube video is dubbed.     |
| `alwaysProxy`                | `boolean` | `true / false`                     | `false`   | tunnels all downloads through the processing server, even when not necessary.   |
| `disableMetadata`            | `boolean` | `true / false`                     | `false`   | disables file metadata when set to `true`.                                      |
| `tiktokFullAudio`            | `boolean` | `true / false`                     | `false`   | enables download of original sound used in a tiktok video.                      |
| `tiktokH265`                 | `boolean` | `true / false`                     | `false`   | changes whether 1080p h265 videos are preferred or not.                         |
| `twitterGif`                 | `boolean` | `true / false`                     | `true`    | changes whether twitter gifs are converted to .gif                              |
| `youtubeHLS`                 | `boolean` | `true / false`                     | `false`   | specifies whether to use HLS for downloading video or audio from youtube.       |

### response
the response will always be a JSON object containing the `status` key, which will be one of:
- `error` - something went wrong
- `picker` - we have multiple items to choose from
- `redirect` - you are being redirected to the direct service URL
- `tunnel` - cobalt is proxying the download for you

### tunnel/redirect response
| key          | type     | values                                                      |
|:-------------|:---------|:------------------------------------------------------------|
| `status`     | `string` | `tunnel / redirect`                                         |
| `url`        | `string` | url for the cobalt tunnel, or redirect to an external link  |
| `filename`   | `string` | cobalt-generated filename for the file being downloaded     |

### picker response
| key             | type     | values                                                                                           |
|:----------------|:---------|:-------------------------------------------------------------------------------------------------|
| `status`        | `string` | `picker`                                                                                         |
| `audio`         | `string` | **optional** returned when an image slideshow (such as on tiktok) has a general background audio |
| `audioFilename` | `string` | **optional** cobalt-generated filename, returned if `audio` exists                               |
| `picker`        | `array`  | array of objects containing the individual media                                                 |

#### picker object
| key          | type      | values                                                      |
|:-------------|:----------|:------------------------------------------------------------|
| `type`       | `string`  | `photo` / `video` / `gif`                                   |
| `url`        | `string`  |                                                             |
| `thumb`      | `string`  | **optional** thumbnail url                                  |

### error response
| key          | type     | values                                                      |
|:-------------|:---------|:------------------------------------------------------------|
| `status`     | `string` | `error`                                                     |
| `error`      | `object` | contains more context about the error                       |

#### error object
| key          | type     | values                                                      |
|:-------------|:---------|:------------------------------------------------------------|
| `code`       | `string` | machine-readable error code explaining the failure reason   |
| `context`    | `object` | **optional** container for providing more context           |

#### error.context object
| key          | type     | values                                                                                                         |
|:-------------|:---------|:---------------------------------------------------------------------------------------------------------------|
| `service`    | `string` | **optional**, stating which service was being downloaded from                                                  |
| `limit`      | `number` | **optional** number providing the ratelimit maximum number of requests, or maximum downloadable video duration |

## GET: `/`
returns current basic server info.
response body type: `application/json`

### response body
| key         | type     | variables                                                |
|:------------|:---------|:---------------------------------------------------------|
| `cobalt`    | `object` | information about the cobalt instance                    |
| `git`       | `object` | information about the codebase that is currently running |

#### cobalt object
| key             | type       | description                                    |
|:----------------|:-----------|:-----------------------------------------------|
| `version`       | `string`   | current version                                |
| `url`           | `string`   | server url                                     |
| `startTime`     | `string`   | server start time in unix milliseconds         |
| `durationLimit` | `number`   | maximum downloadable video length in seconds   |
| `services`      | `string[]` | array of services which this instance supports |

#### git object
| key         | type     | variables         |
|:------------|:---------|:------------------|
| `commit`    | `string` | commit hash       |
| `branch`    | `string` | git branch        |
| `remote`    | `string` | git remote        |

## POST: `/session`

used for generating JWT tokens, if enabled. currently, cobalt only supports
generating tokens when a [turnstile](run-an-instance.md#list-of-all-environment-variables) challenge solution
is submitted by the client.

the turnstile challenge response is submitted via the `cf-turnstile-response` header.
### response body
| key             | type       | description                                            |
|:----------------|:-----------|:-------------------------------------------------------|
| `token`         | `string`   | a `Bearer` token used for later request authentication |
| `exp`           | `number`   | number in seconds indicating the token lifetime        |

on failure, an [error response](#error-response) is returned.


================================================
File: docs/configure-for-youtube.md
================================================
# how to configure a cobalt instance for youtube
if you get various errors when attempting to download videos that are:
publicly available, not region locked, and not age-restricted;
then your instance's ip address may have bad reputation.

in this case you have to use disposable google accounts.
there's no other known workaround as of time of writing this document.

> [!CAUTION]
> **NEVER** use your personal google account for downloading videos via any means.
> you can use any google accounts that you're willing to sacrifice,
> but be prepared to have them **permanently suspended**.
>
> we recommend that you use accounts that don't link back to your personal google account or identity, just in case.
>
> use incognito mode when signing in.
> we also recommend using vpn/proxy services (such as [mullvad](https://mullvad.net/)).

1. if you haven't done it already, clone the cobalt repo, go to the cloned directory, and run `pnpm install`

2. run `pnpm -C api token:youtube`

3. follow instructions, use incognito mode in your browser when signing in.
i cannot stress this enough, but again, **DO NOT USE YOUR PERSONAL GOOGLE ACCOUNT**.

4. once you have the oauth token, add it to `youtube_oauth` in your cookies file.
you can see an [example here](/docs/examples/cookies.example.json).
you can have several account tokens in this file, if you like.

5. all done! enjoy freedom.

### liability
you're responsible for any damage done to any of your google accounts or any other damages. you do this by yourself and at your own risk.


================================================
File: docs/protect-an-instance.md
================================================
# how to protect your cobalt instance
if you keep getting a ton of unknown traffic that hurts the performance of your instance, then it might be a good idea to enable bot protection.

> [!NOTE]
> this tutorial will work reliably on the latest official version of cobalt 10.
we can't promise full compatibility with anything else.

## configure cloudflare turnstile
turnstile is a free, safe, and privacy-respecting alternative to captcha.
cobalt uses it automatically to weed out bots and automated scripts.
your instance doesn't have to be proxied by cloudflare to use turnstile.
all you need is a free cloudflare account to get started.

cloudflare dashboard interface might change over time, but basics should stay the same.

> [!WARNING]
> never share the turnstile secret key, always keep it private. if accidentally exposed, rotate it in widget settings.

1. open [the cloudflare dashboard](https://dash.cloudflare.com/) and log into your account

2. once logged in, select `Turnstile` in the sidebar
<div align="left">
    <p>
        <img src="images/protect-an-instance/sidebar.png" width="250" />
    </p>
</div>

3. press `Add widget`
<div align="left">
    <p>
        <img src="images/protect-an-instance/add.png" width="550" />
    </p>
</div>

4. enter the widget name (can be anything, such as "cobalt")
<div align="left">
    <p>
        <img src="images/protect-an-instance/name.png" width="450" />
    </p>
</div>

5. add cobalt frontend domains you want the widget to work with, you can change this list later at any time
    - if you want to use your processing instance with [cobalt.tools](https://cobalt.tools/) frontend, then add `cobalt.tools` to the list
<div align="left">
    <p>
        <img src="images/protect-an-instance/domain.png" width="450" />
    </p>
</div>

6. select `invisible` widget mode
<div align="left">
    <p>
        <img src="images/protect-an-instance/mode.png" width="450" />
    </p>
</div>

7. press `create`

8. keep the page with sitekey and secret key open, you'll need them later.
if you closed it, no worries!
just open the same turnstile page and press "settings" on your freshly made turnstile widget.

<div align="left">
    <p>
        <img src="images/protect-an-instance/created.png" width="450" />
    </p>
</div>

you've successfully created a turnstile widget!
time to add it to your processing instance.

### enable turnstile on your processing instance
this tutorial assumes that you only have `API_URL` in your `environment` variables list.
if you have other variables there, just add new ones after existing ones.

> [!CAUTION]
> never use any values from the tutorial, especially `JWT_SECRET`!

1. open your `docker-compose.yml` config file in any text editor of choice.
2. copy the turnstile sitekey & secret key and paste them to their respective variables.
`TURNSTILE_SITEKEY` for the sitekey and `TURNSTILE_SECRET` for the secret key:
```yml
environment:
    API_URL: "https://your.instance.url.here.local/"
    TURNSTILE_SITEKEY: "2x00000000000000000000BB" # use your key
    TURNSTILE_SECRET: "2x0000000000000000000000000000000AA" # use your key
```
3. generate a `JWT_SECRET`. we recommend using an alphanumeric collection with a length of at least 64 characters.
this string will be used as salt for all JWT keys.

    you can generate a random secret with `pnpm -r token:jwt` or use any other that you like.

```yml
environment:
    API_URL: "https://your.instance.url.here.local/"
    TURNSTILE_SITEKEY: "2x00000000000000000000BB" # use your key
    TURNSTILE_SECRET: "2x0000000000000000000000000000000AA" # use your key
    JWT_SECRET: "bgBmF4efNCKPirD" # create a new secret, NEVER use this one
```
4. restart the docker container.

## configure api keys
if you want to use your instance outside of web interface, you'll need an api key!

> [!NOTE]
> this tutorial assumes that you'll keep your keys file locally, on the instance server.
> if you wish to upload your file to a remote location,
> replace the value for `API_KEYS_URL` with a direct url to the file
> and skip the second step.

> [!WARNING]
> when storing keys file remotely, make sure that it's not publicly accessible
> and that link to it is either authenticated (via query) or impossible to guess.
>
> if api keys leak, you'll have to update/remove all UUIDs to revoke them.

1. create a `keys.json` file following [the schema and example here](/docs//run-an-instance.md#api-key-file-format).

2. expose the `keys.json` to the docker container:
```yml
volumes:
    - ./keys.json:/keys.json:ro # ro - read-only
```

3. add a path to the keys file to container environment:
```yml
environment:
    # ... other variables here ...
    API_KEY_URL: "file:///keys.json"
```

4. restart the docker container.

## limit access to an instance with api keys but no turnstile
by default, api keys are additional, meaning that they're not *required*,
but work alongside with turnstile or no auth (regular ip hash rate limiting).

to always require auth (via keys or turnstile, if configured), set `API_AUTH_REQUIRED` to 1:
```yml
environment:
    # ... other variables here ...
    API_AUTH_REQUIRED: 1
```

- if both keys and turnstile are enabled, then nothing will change.
- if only keys are configured, then all requests without a valid api key will be refused.

### why not make keys exclusive by default?
keys may be useful for going around rate limiting,
while keeping the rest of api rate limited, with no turnstile in place.


================================================
File: docs/run-an-instance.md
================================================
# how to run a cobalt instance
## using docker compose and package from github (recommended)
to run the cobalt docker package, you need to have `docker` and `docker-compose` installed and configured.

if you need help with installing docker, follow *only the first step* of these tutorials by digitalocean:
- [how to install docker](https://www.digitalocean.com/community/tutorial-collections/how-to-install-and-use-docker)
- [how to install docker compose](https://www.digitalocean.com/community/tutorial-collections/how-to-install-docker-compose)

## how to run a cobalt docker package:
1. create a folder for cobalt config file, something like this:
    ```sh
    mkdir cobalt
    ```

2. go to cobalt folder, and create a docker compose config file:
    ```sh
    cd cobalt && nano docker-compose.yml
    ```
    i'm using `nano` in this example, it may not be available in your distro. you can use any other text editor.

3. copy and paste the [sample config from here](examples/docker-compose.example.yml) for either web or api instance (or both, if you wish) and edit it to your needs.
    make sure to replace default URLs with your own or cobalt won't work correctly.

4. finally, start the cobalt container (from cobalt directory):
    ```sh
    docker compose up -d
    ```

if you want your instance to support services that require authentication to view public content, create `cookies.json` file in the same directory as `docker-compose.yml`. example cookies file [can be found here](examples/cookies.example.json).

cobalt package will update automatically thanks to watchtower.

it's highly recommended to use a reverse proxy (such as nginx) if you want your instance to face the public internet. look up tutorials online.

## run cobalt api outside of docker (useful for local development)
requirements:
- node.js >= 18
- git
- pnpm

1. clone the repo: `git clone https://github.com/imputnet/cobalt`.
2. go to api/src directory: `cd cobalt/api/src`.
3. install dependencies: `pnpm install`.
4. create `.env` file in the same directory.
5. add needed environment variables to `.env` file. only `API_URL` is required to run cobalt.
    - if you don't know what api url to use for local development, use `http://localhost:9000/`.
6. run cobalt: `pnpm start`.

### ubuntu 22.04 workaround
`nscd` needs to be installed and running so that the `ffmpeg-static` binary can resolve DNS ([#101](https://github.com/imputnet/cobalt/issues/101#issuecomment-1494822258)):

```bash
sudo apt install nscd
sudo service nscd start
```

## list of environment variables for api
| variable name         | default   | example                 | description |
|:----------------------|:----------|:------------------------|:------------|
| `API_PORT`            | `9000`    | `9000`                  | changes port from which api server is accessible. |
| `API_LISTEN_ADDRESS`  | `0.0.0.0` | `127.0.0.1`             | changes address from which api server is accessible. **if you are using docker, you usually don't need to configure this.** |
| `API_URL`             | ➖        | `https://api.cobalt.tools/` | changes url from which api server is accessible. <br> ***REQUIRED TO RUN THE API***. |
| `API_NAME`            | `unknown` | `ams-1`                 | api server name that is shown in `/api/serverInfo`. |
| `API_EXTERNAL_PROXY`  | ➖        | `http://user:password@127.0.0.1:8080`| url of the proxy that will be passed to [`ProxyAgent`](https://undici.nodejs.org/#/docs/api/ProxyAgent) and used for all external requests. HTTP(S) only. |
| `CORS_WILDCARD`       | `1`       | `0`                     | toggles cross-origin resource sharing. <br> `0`: disabled. `1`: enabled. |
| `CORS_URL`            | not used  | `https://cobalt.tools`  | cross-origin resource sharing url. api will be available only from this url if `CORS_WILDCARD` is set to `0`. |
| `COOKIE_PATH`         | not used  | `/cookies.json`         | path for cookie file relative to main folder. |
| `PROCESSING_PRIORITY` | not used  | `10`                    | changes `nice` value* for ffmpeg subprocess. available only on unix systems. |
| `FREEBIND_CIDR`       | ➖        | `2001:db8::/32`         | IPv6 prefix used for randomly assigning addresses to cobalt requests. only supported on linux systems. see below for more info. |
| `RATELIMIT_WINDOW`    | `60`      | `120`                   | rate limit time window in **seconds**. |
| `RATELIMIT_MAX`       | `20`      | `30`                    | max requests per time window. requests above this amount will be blocked for the rate limit window duration. |
| `DURATION_LIMIT`      | `10800`   | `18000`                 | max allowed video duration in **seconds**. |
| `TUNNEL_LIFESPAN`     | `90`      | `120`                   | the duration for which tunnel info is stored in ram, **in seconds**. |
| `TURNSTILE_SITEKEY`   | ➖        | `1x00000000000000000000BB` | [cloudflare turnstile](https://www.cloudflare.com/products/turnstile/) sitekey used by browser clients to request a challenge.\*\* |
| `TURNSTILE_SECRET`    | ➖        | `1x0000000000000000000000000000000AA` | [cloudflare turnstile](https://www.cloudflare.com/products/turnstile/) secret used by cobalt to verify the client successfully solved the challenge.\*\* |
| `JWT_SECRET`          | ➖        | ➖                      | the secret used for issuing JWT tokens for request authentication. to choose a value, generate a random, secure, long string (ideally >=16 characters).\*\* |
| `JWT_EXPIRY`          | `120`     | `240`                  | the duration of how long a cobalt-issued JWT token will remain valid, in seconds. |
| `API_KEY_URL`         | ➖        | `file://keys.json`      | the location of the api key database. for loading API keys, cobalt supports HTTP(S) urls, or local files by specifying a local path using the `file://` protocol. see the "api key file format" below for more details.  |
| `API_AUTH_REQUIRED`   | ➖        | `1`                     | when set to `1`, the user always needs to be authenticated in some way before they can access the API (either via an api key or via turnstile, if enabled). |
| `API_REDIS_URL`       | ➖        | `redis://localhost:6379` | when set, cobalt uses redis instead of internal memory for the tunnel cache. |
| `API_INSTANCE_COUNT`  | ➖        | `2`                     | supported only on Linux and node.js `>=23.1.0`. when configured, cobalt will spawn multiple sub-instances amongst which requests will be balanced. |
| `DISABLED_SERVICES`   | ➖        | `bilibili,youtube`       | comma-separated list which disables certain services from being used. |

\* the higher the nice value, the lower the priority. [read more here](https://en.wikipedia.org/wiki/Nice_(Unix)).

\*\* in order to enable turnstile bot protection, all three **`TURNSTILE_SITEKEY`, `TURNSTILE_SECRET` and `JWT_SECRET`** need to be set.

#### FREEBIND_CIDR
setting a `FREEBIND_CIDR` allows cobalt to pick a random IP for every download and use it for all
requests it makes for that particular download. to use freebind in cobalt, you need to follow its [setup instructions](https://github.com/imputnet/freebind.js?tab=readme-ov-file#setup) first. if you configure this option while running cobalt
in a docker container, you also need to set the `API_LISTEN_ADDRESS` env to `127.0.0.1`, and set
`network_mode` for the container to `host`.

## api key file format
the file is a JSON-serialized object with the following structure:
```typescript

type KeyFileContents = Record<
    UUIDv4String,
    {
        name?: string,
        limit?: number | "unlimited",
        ips?: (CIDRString | IPString)[],
        userAgents?: string[]
    }
>;
```

where *`UUIDv4String`* is a stringified version of a UUIDv4 identifier.
- **name** is a field for your own reference, it is not used by cobalt anywhere.

- **`limit`** specifies how many requests the API key can make during the window specified in the `RATELIMIT_WINDOW` env.
    - when omitted, the limit specified in `RATELIMIT_MAX` will be used.
    - it can be also set to `"unlimited"`, in which case the API key bypasses all rate limits.

- **`ips`** contains an array of allowlisted IP ranges, which can be specified both as individual ips or CIDR ranges (e.g. *`["192.168.42.69", "2001:db8::48", "10.0.0.0/8", "fe80::/10"]`*).
    - when specified, only requests from these ip ranges can use the specified api key.
    - when omitted, any IP can be used to make requests with that API key.

- **`userAgents`** contains an array of allowed user agents, with support for wildcards (e.g. *`["cobaltbot/1.0", "Mozilla/5.0 * Chrome/*"]`*).
    - when specified, requests with a `user-agent` that does not appear in this array will be rejected.
    - when omitted, any user agent can be specified to make requests with that API key.

- if both `ips` and `userAgents` are set, the tokens will be limited by both parameters.
- if cobalt detects any problem with your key file, it will be ignored and a warning will be printed to the console.

an example key file could look like this:
```json
{
    "b5c7160a-b655-4c7a-b500-de839f094550": {
        "limit": 10,
        "ips": ["10.0.0.0/8", "192.168.42.42"],
        "userAgents": ["*Chrome*"]
    },
    "b00b1234-a3e5-99b1-c6d1-dba4512ae190": {
        "limit": "unlimited",
        "ips": ["192.168.1.2"],
        "userAgents": ["cobaltbot/1.0"]
    }
}
```

if you are configuring a key file, **do not use the UUID from the example** but instead generate your own. you can do this by running the following command if you have node.js installed:
`node -e "console.log(crypto.randomUUID())"`


================================================
File: docs/examples/cookies.example.json
================================================
{
    "instagram": [
        "mid=<replace>; ig_did=<with>; csrftoken=<your>; ds_user_id=<own>; sessionid=<cookies>"
    ],
    "instagram_bearer": [
        "token=<token_with_no_bearer_in_front>", "token=IGT:2:<looks_like_this>"
    ],
    "reddit": [
        "client_id=<replace_this>; client_secret=<replace_this>; refresh_token=<replace_this>"
    ],
    "twitter": [
        "auth_token=<replace_this>; ct0=<replace_this>"
    ],
    "youtube_oauth": [
        "<output from running `pnpm run token:youtube` in `api` folder goes here>"
    ]
}


================================================
File: docs/examples/docker-compose.example.yml
================================================
services:
    cobalt-api:
        image: ghcr.io/imputnet/cobalt:10

        init: true
        read_only: true
        restart: unless-stopped
        container_name: cobalt-api

        ports:
            - 9000:9000/tcp
            # if you use a reverse proxy (such as nginx),
            # uncomment the next line and remove the one above (9000:9000/tcp):
            # - 127.0.0.1:9000:9000

        environment:
            # replace https://api.url.example/ with your instance's url
            # or else tunneling functionality won't work properly
            API_URL: "https://api.url.example/"

            # if you want to use cookies for fetching data from services,
            # uncomment the next line & volumes section
            # COOKIE_PATH: "/cookies.json"

            # it's recommended to configure bot protection or api keys if the instance is public,
            # see /docs/protect-an-instance.md for more info

            # see /docs/run-an-instance.md for more variables that you can use here

        labels:
            - com.centurylinklabs.watchtower.scope=cobalt

        # uncomment only if you use the COOKIE_PATH variable
        # volumes:
            # - ./cookies.json:/cookies.json

    # watchtower updates the cobalt image automatically
    watchtower:
        image: ghcr.io/containrrr/watchtower
        restart: unless-stopped
        command: --cleanup --scope cobalt --interval 900 --include-restarting
        volumes:
            - /var/run/docker.sock:/var/run/docker.sock



<h1 align="center">
  <br>
  <a href="https://gremlin.codes"><img src="https://raw.githubusercontent.com/therealjr/gremlincodes/main/gremlin.png" alt="Gremlin.Codes" width="200"></a>
  <br>
  Gremlin.Codes
  <br>
  <br>
</h1>

<h4 align="center">Decentralized forum and video streaming platform for the web.</h4>

<p align="center">
  <a href="https://discord.gg/cnXkm4Z"><img src="https://img.shields.io/discord/612575111718895616" alt="discord"></a>
</p>


<br>

**Gremlin.Codes** is a **forum** and **streaming service** for the **browser**. 


### Features
- **Decentralized**
- Uses **Web3** technology!
- **Insanely fast**
- Uses **bittorrent** tracker servers for static file distribution
- Download **multiple torrents** simultaneously, efficiently

### Install

To install WebTorrent for use in node or the browser with `import WebTorrent from 'webtorrent'`, run:

```bash
npm install webtorrent
```

To install a `webtorrent`
[command line program](https://github.com/webtorrent/webtorrent-cli), run:

```bash
npm install webtorrent-cli -g
```

To install a WebTorrent desktop application for Mac, Windows, or Linux, see
[WebTorrent Desktop][webtorrent-desktop].

### Ways to help

- **Join us in [Gitter][webtorrent-gitter-url]** or on freenode at `#webtorrent` to help
  with development or to hang out with some mad science hackers :)
- **[Create a new issue](https://github.com/webtorrent/webtorrent/issues/new)** to report bugs
- **[Fix an issue](https://github.com/webtorrent/webtorrent/issues?state=open)**. WebTorrent
  is an [OPEN Open Source Project](https://github.com/webtorrent/.github/blob/master/CONTRIBUTING.md)!

### Who is using WebTorrent today?

**[Lots of folks!](docs/faq.md#who-is-using-webtorrent-today)**

### WebTorrent API Documentation

**[Read the full API Documentation](docs/api.md).**

### Usage

WebTorrent is the first BitTorrent client that works in the browser, using open web
standards (no plugins, just HTML5 and WebRTC)! It's easy to get started!

#### In the browser

##### Downloading a file is simple:

```js
import WebTorrent from 'webtorrent'

const client = new WebTorrent()
const magnetURI = '...'

client.add(magnetURI, torrent => {
  // Got torrent metadata!
  console.log('Client is downloading:', torrent.infoHash)

  for (const file of torrent.files) {
    document.body.append(file.name)
  }
})
```

##### Seeding a file is simple, too:

```js
import dragDrop from 'drag-drop'
import WebTorrent from 'webtorrent'

const client = new WebTorrent()

// When user drops files on the browser, create a new torrent and start seeding it!
dragDrop('body', files => {
  client.seed(files, torrent => {
    console.log('Client is seeding:', torrent.infoHash)
  })
})
```

There are more examples in [docs/get-started.md](docs/get-started.md).

##### Browserify

WebTorrent works great with [browserify](http://browserify.org/), an npm package that lets
you use [node](http://nodejs.org/)-style require() to organize your browser code and load modules installed by [npm](https://www.npmjs.com/) (as seen in the previous examples).

##### Webpack

WebTorrent also works with [webpack](https://webpack.js.org/), another module
bundler. However, webpack requires extra configuration which you can find in [the webpack bundle config used by webtorrent](/scripts/browser.webpack.js).


Or, you can just use the pre-built version via
`import WebTorrent from 'webtorrent/dist/webtorrent.min.js'` and skip the webpack configuration.

##### Script tag

WebTorrent is also available as a standalone script
([`webtorrent.min.js`](webtorrent.min.js)) which exposes `WebTorrent` on the `window`
object, so it can be used with just a script tag:

```html
<script type='module'>
  import WebTorrent from 'webtorrent.min.js'
</script>
```

The WebTorrent script is also hosted on fast, reliable CDN infrastructure (Cloudflare and
MaxCDN) for easy inclusion on your site:

```html
<script type='module'>
  import WebTorrent from 'https://esm.sh/webtorrent'
</script>
```

##### Chrome App

If you want to use WebTorrent in a
[Chrome App](https://developer.chrome.com/apps/about_apps), you can include the
following script:

```html
<script type='module'>
  import WebTorrent from 'webtorrent.chromeapp.js'
</script>
```

Be sure to enable the `chrome.sockets.udp` and `chrome.sockets.tcp` permissions!

#### In Node.js

WebTorrent also works in node.js, using the *same npm package!* It's mad science!

**NOTE**: To connect to "web peers" (browsers) in addition to normal BitTorrent peers, use
[webtorrent-hybrid](https://github.com/webtorrent/webtorrent-hybrid) which includes WebRTC
support for node.

#### As a command line app

WebTorrent is also available as a
[command line app](https://github.com/webtorrent/webtorrent-cli). Here's how to use it:

```bash
$ npm install webtorrent-cli -g
$ webtorrent --help
```

To download a torrent:

```bash
$ webtorrent magnet_uri
```

To stream a torrent to a device like **AirPlay** or **Chromecast**, just pass a flag:

```bash
$ webtorrent magnet_uri --airplay
```

There are many supported streaming options:

```bash
--airplay               Apple TV
--chromecast            Chromecast
--mplayer               MPlayer
--mpv                   MPV
--omx [jack]            omx [default: hdmi]
--vlc                   VLC
--xbmc                  XBMC
--stdout                standard out [implies --quiet]
```

In addition to magnet uris, WebTorrent supports [many ways](docs/api.md#clientaddtorrentid-opts-function-ontorrent-torrent-) to specify a torrent.

### Talks about WebTorrent

- Sep 2017 - Nordic JS - [Get Rich Quick With P2P Crypto Currency](https://www.youtube.com/watch?v=8N_4Furztjo)
- May 2017 - Char.la - [WebTorrent and Peerify](https://youtu.be/D-04vg5hvEQ?t=54m20s) (Spanish)
- Nov 2016 - NodeConf Argentina - [Real world Electron: Building Cross-platform desktop apps with JavaScript](https://www.youtube.com/watch?v=YLExGgEnbFY)
- May 2016 - SIGNAL Conference - [BitTorrent in the Browser](https://www.youtube.com/watch?v=2qrUx-C5Np4)
- May 2015 - Data Terra Nemo - [WebTorrent: Mother of all demos](https://www.youtube.com/watch?v=RRtNEcAaUO8)
- May 2015 - Data Terra Nemo - [WebRTC Everywhere](https://www.youtube.com/watch?v=RRtNEcAaUO8)
- Nov 2014 - JSConf Asia - [How WebTorrent Works](https://www.youtube.com/watch?v=kxHRATfvnlw)
- Sep 2014 - NodeConf EU - [WebRTC Mad Science](https://www.youtube.com/watch?v=BVBXkzVjvPc) (first working WebTorrent demo)
- Apr 2014 - CraftConf - [Bringing BitTorrent to the Web](https://www.youtube.com/watch?v=PT8s_IVWDgw)
- May 2014 - JS.LA - [How I Built a BitTorrent Client in the Browser](https://vimeo.com/97324247) (progress update; node client working)
- Oct 2013 - RealtimeConf - [WebRTC Black Magic](https://vimeo.com/77265280) (first mention of idea for WebTorrent)

### Modules

Most of the active development is happening inside of small npm packages which are used by WebTorrent.

#### The Node Way&trade;

> "When applications are done well, they are just the really application-specific, brackish residue that can't be so easily abstracted away. All the nice, reusable components sublimate away onto github and npm where everybody can collaborate to advance the commons." — substack from ["how I write modules"](https://gist.github.com/substack/5075355)

![node.js is shiny](https://feross.net/x/node2.gif)

#### Modules

These are the main modules that make up WebTorrent:

| module | tests | version | description |
|---|---|---|---|
| **[webtorrent][webtorrent]** | [![][webtorrent-ti]][webtorrent-tu] | [![][webtorrent-ni]][webtorrent-nu] | **torrent client (this module)**
| [bittorrent-dht][bittorrent-dht] | [![][bittorrent-dht-ti]][bittorrent-dht-tu] | [![][bittorrent-dht-ni]][bittorrent-dht-nu] | distributed hash table client
| [bittorrent-peerid][bittorrent-peerid] | [![][bittorrent-peerid-ti]][bittorrent-peerid-tu] | [![][bittorrent-peerid-ni]][bittorrent-peerid-nu] | identify client name/version
| [bittorrent-protocol][bittorrent-protocol] | [![][bittorrent-protocol-ti]][bittorrent-protocol-tu] | [![][bittorrent-protocol-ni]][bittorrent-protocol-nu] | bittorrent protocol stream
| [bittorrent-tracker][bittorrent-tracker] | [![][bittorrent-tracker-ti]][bittorrent-tracker-tu] | [![][bittorrent-tracker-ni]][bittorrent-tracker-nu] | bittorrent tracker server/client
| [bittorrent-lsd][bittorrent-lsd] | [![][bittorrent-lsd-ti]][bittorrent-lsd-tu] | [![][bittorrent-lsd-ni]][bittorrent-lsd-nu] | bittorrent local service discovery
| [create-torrent][create-torrent] | [![][create-torrent-ti]][create-torrent-tu] | [![][create-torrent-ni]][create-torrent-nu] | create .torrent files
| [magnet-uri][magnet-uri] | [![][magnet-uri-ti]][magnet-uri-tu] | [![][magnet-uri-ni]][magnet-uri-nu] | parse magnet uris
| [parse-torrent][parse-torrent] | [![][parse-torrent-ti]][parse-torrent-tu] | [![][parse-torrent-ni]][parse-torrent-nu] | parse torrent identifiers
| [torrent-discovery][torrent-discovery] | [![][torrent-discovery-ti]][torrent-discovery-tu] | [![][torrent-discovery-ni]][torrent-discovery-nu] | find peers via dht, tracker, and lsd
| [ut_metadata][ut_metadata] | [![][ut_metadata-ti]][ut_metadata-tu] | [![][ut_metadata-ni]][ut_metadata-nu] | metadata for magnet uris (protocol extension)
| [ut_pex][ut_pex] | [![][ut_pex-ti]][ut_pex-tu] | [![][ut_pex-ni]][ut_pex-nu] | peer discovery (protocol extension)

[webtorrent]: https://github.com/webtorrent/webtorrent
[webtorrent-gitter-url]: https://gitter.im/webtorrent/webtorrent

[webtorrent-ti]: https://img.shields.io/github/actions/workflow/status/webtorrent/webtorrent/ci.yml
[webtorrent-tu]: https://github.com/webtorrent/webtorrent/actions
[webtorrent-ni]: https://img.shields.io/npm/v/webtorrent.svg
[webtorrent-nu]: https://www.npmjs.com/package/webtorrent
[webtorrent-desktop]: https://webtorrent.io/desktop

[bittorrent-dht]: https://github.com/webtorrent/bittorrent-dht
[bittorrent-dht-ti]: https://img.shields.io/github/actions/workflow/status/webtorrent/bittorrent-dht/ci.yml?branch=master
[bittorrent-dht-tu]: https://github.com/webtorrent/bittorrent-dht/actions
[bittorrent-dht-ni]: https://img.shields.io/npm/v/bittorrent-dht.svg
[bittorrent-dht-nu]: https://www.npmjs.com/package/bittorrent-dht

[bittorrent-peerid]: https://github.com/webtorrent/bittorrent-peerid
[bittorrent-peerid-ti]: https://img.shields.io/github/actions/workflow/status/webtorrent/bittorrent-peerid/ci.yml?branch=master
[bittorrent-peerid-tu]: https://github.com/webtorrent/bittorrent-peerid/actions
[bittorrent-peerid-ni]: https://img.shields.io/npm/v/bittorrent-peerid.svg
[bittorrent-peerid-nu]: https://www.npmjs.com/package/bittorrent-peerid

[bittorrent-protocol]: https://github.com/webtorrent/bittorrent-protocol
[bittorrent-protocol-ti]: https://img.shields.io/github/actions/workflow/status/webtorrent/bittorrent-protocol/ci.yml?branch=master
[bittorrent-protocol-tu]: https://github.com/webtorrent/bittorrent-protocol/actions
[bittorrent-protocol-ni]: https://img.shields.io/npm/v/bittorrent-protocol.svg
[bittorrent-protocol-nu]: https://www.npmjs.com/package/bittorrent-protocol

[bittorrent-tracker]: https://github.com/webtorrent/bittorrent-tracker
[bittorrent-tracker-ti]: https://img.shields.io/github/actions/workflow/status/webtorrent/bittorrent-tracker/ci.yml?branch=master
[bittorrent-tracker-tu]: https://github.com/webtorrent/bittorrent-tracker/actions
[bittorrent-tracker-ni]: https://img.shields.io/npm/v/bittorrent-tracker.svg
[bittorrent-tracker-nu]: https://www.npmjs.com/package/bittorrent-tracker

[bittorrent-lsd]: https://github.com/webtorrent/bittorrent-lsd
[bittorrent-lsd-ti]: https://img.shields.io/github/actions/workflow/status/webtorrent/bittorrent-lsd/ci.yml?branch=master
[bittorrent-lsd-tu]: https://github.com/webtorrent/bittorrent-lsd/actions
[bittorrent-lsd-ni]: https://img.shields.io/npm/v/bittorrent-lsd.svg
[bittorrent-lsd-nu]: https://www.npmjs.com/package/bittorrent-lsd

[create-torrent]: https://github.com/webtorrent/create-torrent
[create-torrent-ti]: https://img.shields.io/github/actions/workflow/status/webtorrent/create-torrent/ci.yml?branch=master
[create-torrent-tu]: https://github.com/webtorrent/create-torrent/actions
[create-torrent-ni]: https://img.shields.io/npm/v/create-torrent.svg
[create-torrent-nu]: https://www.npmjs.com/package/create-torrent

[magnet-uri]: https://github.com/webtorrent/magnet-uri
[magnet-uri-ti]: https://img.shields.io/github/actions/workflow/status/webtorrent/magnet-uri/ci.yml?branch=master
[magnet-uri-tu]: https://github.com/webtorrent/magnet-uri/actions
[magnet-uri-ni]: https://img.shields.io/npm/v/magnet-uri.svg
[magnet-uri-nu]: https://www.npmjs.com/package/magnet-uri

[parse-torrent]: https://github.com/webtorrent/parse-torrent
[parse-torrent-ti]: https://img.shields.io/github/actions/workflow/status/webtorrent/parse-torrent/ci.yml?branch=master
[parse-torrent-tu]: https://github.com/webtorrent/parse-torrent/actions
[parse-torrent-ni]: https://img.shields.io/npm/v/parse-torrent.svg
[parse-torrent-nu]: https://www.npmjs.com/package/parse-torrent

[torrent-discovery]: https://github.com/webtorrent/torrent-discovery
[torrent-discovery-ti]: https://img.shields.io/github/actions/workflow/status/webtorrent/torrent-discovery/ci.yml?branch=master
[torrent-discovery-tu]: https://github.com/webtorrent/torrent-discovery/actions
[torrent-discovery-ni]: https://img.shields.io/npm/v/torrent-discovery.svg
[torrent-discovery-nu]: https://www.npmjs.com/package/torrent-discovery

[ut_metadata]: https://github.com/webtorrent/ut_metadata
[ut_metadata-ti]: https://img.shields.io/github/actions/workflow/status/webtorrent/ut_metadata/ci.yml?branch=master
[ut_metadata-tu]: https://github.com/webtorrent/ut_metadata/actions
[ut_metadata-ni]: https://img.shields.io/npm/v/ut_metadata.svg
[ut_metadata-nu]: https://www.npmjs.com/package/ut_metadata

[ut_pex]: https://github.com/webtorrent/ut_pex
[ut_pex-ti]: https://img.shields.io/github/actions/workflow/status/webtorrent/ut_pex/ci.yml?branch=master
[ut_pex-tu]: https://github.com/webtorrent/ut_pex/actions
[ut_pex-ni]: https://img.shields.io/npm/v/ut_pex.svg
[ut_pex-nu]: https://www.npmjs.com/package/ut_pex

#### Enable debug logs

In **node**, enable debug logs by setting the `DEBUG` environment variable to the name of the
module you want to debug (e.g. `bittorrent-protocol`, or `*` to print **all logs**).

```bash
DEBUG=* webtorrent
```

In the **browser**, enable debug logs by running this in the developer console:

```js
localStorage.setItem('debug', '*')
```

Disable by running this:

```js
localStorage.removeItem('debug')
```

### License

MIT. Copyright (c) [Feross Aboukhadijeh](https://feross.org) and [WebTorrent, LLC](https://webtorrent.io).
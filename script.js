window.onSpotifyWebPlaybackSDKReady = () => {
  const token = "[My Spotify Web API access token]";
  const player = new Spotify.Player({
    name: "Web Playback SDK Quick Start Player",
    getOAuthToken: (cb) => {
      cb(token);
    },
  });
};

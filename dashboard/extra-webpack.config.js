const singleSpaAngularWebpack = require('single-spa-angular/lib/webpack').default;

module.exports = (config, options) => {
  const singleSpaWebpackConfig = singleSpaAngularWebpack(config, options);

  singleSpaWebpackConfig.devServer = {
    ...(singleSpaWebpackConfig.devServer || {}),
    headers: {
      "Access-Control-Allow-Origin": "*",
    },
  };
  // Feel free to modify this webpack config however you'd like to
  return singleSpaWebpackConfig;
};

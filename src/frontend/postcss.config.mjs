/**
 * PostCSS configuration.
 *
 * postcss-px-to-viewport-8-plugin converts px → vw for a 375px mobile design.
 * Only applies to Vant components and MobileLayout to avoid affecting the
 * PC layout where fixed px values are needed.
 */
export default {
  plugins: {
    'postcss-px-to-viewport-8-plugin': {
      viewportWidth: 375,
      unitPrecision: 5,
      viewportUnit: 'vw',
      fontViewportUnit: 'vw',
      selectorBlackList: ['.pc-'],
      minPixelValue: 1,
      mediaQuery: false,
      replace: true,
      include: [/\/node_modules\/vant\//, /\/layouts\/Mobile/],
    },
  },
}

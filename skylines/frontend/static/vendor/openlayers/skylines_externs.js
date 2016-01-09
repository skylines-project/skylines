/**
 * @interface
 */
oli.format.JSONFeature = function() {};

/**
 * @param {Object} object Object.
 * @param {olx.format.ReadOptions=} opt_options Options.
 * @return {Array.<ol.Feature>} Feature.
 */
oli.format.JSONFeature.prototype.readFeaturesFromObject = function(object, opt_options) {};

/**
 * @param {Object} object Object.
 * @param {olx.format.ReadOptions=} opt_options Options.
 * @return {ol.Feature} Feature.
 */
oli.format.JSONFeature.prototype.readFeatureFromObject = function(object, opt_options) {};

/**
 * @param {Object} object Object.
 * @return {ol.proj.Projection} Projection.
 */
oli.format.JSONFeature.prototype.readProjectionFromObject = function(object) {};

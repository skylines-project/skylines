var slTaskPanel = Backbone.View.extend({
  turnpoints: null,

  /**
   * Renders the task panel into the placeholder.
   */
  render: function() {
    this.$el.html('');

    // Loop through data and render each one
    this.turnpoints.each(function(turnpoint) {
      var turnpoint_view = new slTaskPanelTurnpointView({
        model: turnpoint
      });

      this.$el.append(turnpoint_view.el);
    }.bind(this));

    return this;
  },

  setTask: function(task) {
    this.model = task;
    this.turnpoints = task.getTurnpoints();

    // Listen to changes in the turnpoint collection
    this.listenTo(this.turnpoints, 'add', this.render);
    this.listenTo(this.turnpoints, 'remove', this.render);

    this.render();
  }
});

var slTaskPanelTurnpointView = Backbone.View.extend({
  tagName: 'div',

  attributes: {
    'class': 'turnpoint'
  },

  events: {
    'mouseover': 'highlight',
    'mouseout': 'unhighlight'
  },

  initialize: function() {
    this.render();
    this.listenTo(this.model, 'change:coordinate', this.render);

    this.listenTo(this.model.getSector(), 'change:highlight', function(state) {
      if (state) this.$el.addClass('highlight');
      else this.$el.removeClass('highlight');
    });
  },

  render: function() {
    var html = $(
      '<div class="sector ' + this.sectorSprite() + '"></div>' +
      '<p class="title">' +
        this.formatTitle() +
      '</p>' +
      '<p class="coordinates">' +
        this.formatCoordinates() +
      '</p>' +
      '<p class="type">' +
        this.formatType() +
      '</p>');

    this.$el.html(html);
  },

  highlight: function() {
    this.model.getSector().highlight(true);
  },

  unhighlight: function() {
    this.model.getSector().highlight(false);
  },

  formatTitle: function() {
    var name = '';
    var position = '';

    if (this.model.getWaypoint()) {
      name = this.model.getWaypoint().getName();
    } else {
      name = 'Free Turnpoint';
    }

    var index = this.model.collection.indexOf(this.model);

    if (index == 0) {
      position = 'Start';
    } else if (index == this.model.collection.length - 1) {
      position = 'Finish';
    } else {
      position = 'WP ' + index;
    }

    return position + ': ' + name;
  },

  formatCoordinates: function() {
    var epsg4326 = ol.proj.toLonLat(this.model.getCoordinate());
    return ol.coordinate.toStringHDMS(epsg4326);
  },

  formatType: function() {
    var name = this.model.getSector().getName();
    var props = this.model.getSector().getProperties();

    var format_props = [];

    if ('radius' in props)
      format_props.push('R = ' + props.radius);

    if ('inner_radius' in props)
      format_props.push('Ri = ' + props.inner_radius);

    if ('start_radial' in props)
      format_props.push('from: ' + props.start_radial);

    if ('end_radial' in props)
      format_props.push('to: ' + props.end_radial);

    if (format_props)
      name += ', ' + format_props.join(', ');

    return name;
  },

  sectorSprite: function() {
    return this.model.getSector().getType();
  }
});

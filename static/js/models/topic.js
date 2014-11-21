/**
 * Corresponds to the /grammar/ endpoint in the API.
 */
define(['jquery', 
	'underscore', 
	'backbone', 
	'utils'], 
	function($, _, Backbone, Utils) {

		return Backbone.Model.extend({
			defaults: {
				'modelName': 'topic',
			},
			url: function() {
				return this.get('resource_uri');
			},
			parse: function(response) {
				if (response && response.meta) {
					this.meta = response.meta;
				}

				this.set(response);

			},
			sortTasks: function() {
				if (!this.get('task_sequence')) return;

				// Sort task sequence by order
				this.get('task_sequence').tasks = _.sortBy(this.get('task_sequence').tasks, function(task) {
					return task.order;
				});
			},
			getCurrentTask: function() {
				var i = this.get('currentTaskIndex');
				var seq = this.get('task_sequence');

				return seq.tasks.filter(function(task) {
					return task.order === i;
				})[0];
			}
		}
	);
});

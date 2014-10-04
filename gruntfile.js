module.exports = function(grunt) {
	grunt.initConfig({
		pkg: grunt.file.readJSON('package.json'),
		sass: {
			dist: {
				files: {
					'static/css/create.ltr.css': 'static/css/create.scss',
					'static/css/index.ltr.css': 'static/css/index.scss',
					'static/css/lessons.ltr.css': 'static/css/lessons.scss',
					'static/css/profile.ltr.css': 'static/css/profile.scss',
					'static/css/reader.ltr.css': 'static/css/reader.scss'
				}
			}
		},
		watch: {
			css: {
				files: 'static/css/*.scss',
				tasks: ['sass']
			}
		}
	});
	grunt.loadNpmTasks('grunt-contrib-sass');
	grunt.loadNpmTasks('grunt-contrib-watch');
	grunt.registerTask('default', ['watch']);
}

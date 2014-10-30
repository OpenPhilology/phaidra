module.exports = function(grunt) {
	grunt.initConfig({
		pkg: grunt.file.readJSON('package.json'),
		sass: {
			ltr: {
				options: {
					style: 'compressed'
				},
				files: {
					'static/css/ltr/create.css': 'static/css/create.scss',
					'static/css/ltr/index.css': 'static/css/index.scss',
					'static/css/ltr/lessons.css': 'static/css/lessons.scss',
					'static/css/ltr/profile.css': 'static/css/profile.scss',
					'static/css/ltr/reader.css': 'static/css/reader.scss'
				}
			},
			rtl: {
				options: {
					style: 'compressed'
				},
				files: {
					'static/css/rtl/create.css': 'static/css/create.scss',
					'static/css/rtl/index.css': 'static/css/index.scss',
					'static/css/rtl/lessons.css': 'static/css/lessons.scss',
					'static/css/rtl/profile.css': 'static/css/profile.scss',
					'static/css/rtl/reader.css': 'static/css/reader.scss'
				}
			}
		},
		concat: {
			ltrCSS: {
				src: ['static/css/dirs/ltr.scss', 'static/css/_dir.scss'],
				dest: 'static/css/_directional.scss'
			},
			rtlCSS: {
				src: ['static/css/dirs/rtl.scss', 'static/css/_dir.scss'],
				dest: 'static/css/_directional.scss'
			}
		},
		watch: {
			ltrCSS: {
				files: 'static/css/*.scss',
				tasks: ['concat:ltrCSS', 'sass:ltr']
			},
			rtlCSS: {
				files: 'static/css/*.scss',
				tasks: ['concat:rtlCSS', 'sass:rtl']
			}
		}
	});
	grunt.loadNpmTasks('grunt-contrib-concat');
	grunt.loadNpmTasks('grunt-contrib-sass');
	grunt.loadNpmTasks('grunt-contrib-watch');
	grunt.registerTask('default', ['watch']);
}

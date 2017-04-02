// Los packages que vamos a usar
var gulp  = require('gulp'),
	gutil = require('gulp-util'),
	sass = require('gulp-sass'),
	cssnano = require('gulp-cssnano'),
	autoprefixer = require('gulp-autoprefixer'),
	sourcemaps = require('gulp-sourcemaps'),
	jshint = require('gulp-jshint'),
	stylish = require('jshint-stylish'),
	uglify = require('gulp-uglify'),
	concat = require('gulp-concat'),
	rename = require('gulp-rename'),
	plumber = require('gulp-plumber'),
	bower = require('gulp-bower'),
	browserSync = require('browser-sync').create();
	modRewrite = require('connect-modrewrite');
	gettext = require('gulp-angular-gettext');


// Compilar SASS, poner auto-prefijos, minimizar
gulp.task('styles', function() {
	return gulp.src('./bootstrap.scss') // ¿Dónde están los archivos fuentes?
		.pipe(plumber(function(error) { // Así podemos ver errores en el terminal
				gutil.log(gutil.colors.red(error.message));
				this.emit('end');
		}))
		.pipe(sourcemaps.init()) // Start Sourcemaps
		.pipe(sass())
		.pipe(autoprefixer({
				browsers: ['last 2 versions'],
				cascade: false
		}))
		.pipe(gulp.dest('./static/css/'))
		.pipe(rename({suffix: '.min'}))
		.pipe(cssnano())
		.pipe(sourcemaps.write('.')) // Creates sourcemaps for minified styles
		.pipe(gulp.dest('./dist/css/'))
});
		






// Watch files for changes (without Browser-Sync)
gulp.task('watch', function() {

	// Watch .scss files
	gulp.watch('./_variables.scss', ['styles']);


}); 

// Run styles, site-js and bootstrap-js
gulp.task('default', function() {
	gulp.start('styles');
});




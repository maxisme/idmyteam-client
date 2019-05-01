$(document).ready(function(){
	$("#sub").css("right", $(window).width() / 2 - $("#sub").width() / 2);

    /* for nav bar */
	$(".button-collapse").sideNav();

    /* Replace all SVG images with inline SVG */
    jQuery('img.svg').each(function(){
        var $img = jQuery(this);
        var imgID = $img.attr('id');
        var imgClass = $img.attr('class');
        var imgURL = $img.attr('src');

        jQuery.get(imgURL, function(data) {
            // Get the SVG tag, ignore the rest
            var $svg = jQuery(data).find('svg');
            // Add replaced image's ID to the new SVG
            if(typeof imgID !== 'undefined') {
                $svg = $svg.attr('id', imgID);
            }
            // Add replaced image's classes to the new SVG
            if(typeof imgClass !== 'undefined') {
                $svg = $svg.attr('class', imgClass+' replaced-svg');
            }
            // Remove any invalid XML tags as per http://validator.w3.org
            $svg = $svg.removeAttr('xmlns:a');
            // Replace image with new SVG
            $img.replaceWith($svg);

        }, 'xml');
    });

    /* materialize */
    $('.modal').modal();
	$('select').material_select();

    function fadeInOut() {
        var el = $(".flashme");
        el.animate({opacity:'0.2'}, 1000);
        el.animate({opacity:'1'}, 1000, fadeInOut);
    }

    fadeInOut();
});

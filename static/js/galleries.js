$(document).ready(function(){
    $("[id^=toggle_exif]").click(function(){
        $("[id^=exif_data]").fadeToggle();
    });

    $("#carousel_prev").click(function(){
        $("[id^=form]").hide();
        $("[id^=title]").hide();
        $("[id^=buttons]").hide();
        $("[id^=exifdiv]").hide();

        nextSlide = $('.carousel-item.active').prev("div[data-carouselimage='yes']").data('imageid');
        if(nextSlide == undefined)
            nextSlide = $("div[data-carouselimage='yes']").last().data('imageid');

        $("#form" + nextSlide).show();
        $("#title" + nextSlide).show();
        $("#buttons" + nextSlide).show();
        $("#exifdiv" + nextSlide).show();
        $("[id^=map]").hide();
    });
    
    $("#carousel_next").click(function(){
        $("[id^=form]").hide();
        $("[id^=title]").hide();
        $("[id^=buttons]").hide();
        $("[id^=exifdiv]").hide();

        nextSlide = $('.carousel-item.active').next("div[data-carouselimage='yes']").data('imageid');
        if(nextSlide == undefined)
            nextSlide = $("div[data-carouselimage='yes']").first().data('imageid');
        
        $("#form"+nextSlide).show();
        $("#title"+nextSlide).show();
        $("#buttons" + nextSlide).show();
        $("#exifdiv" + nextSlide).show();
        $("[id^=map]").hide();
    });
    
});

function getNext(){
    nextSlide = $('.carousel-item.active').next("div[data-carouselimage='yes']").data('imageid');
    if(nextSlide == undefined)
        nextSlide = $("div[data-carouselimage='yes']").first().data('imageid');
    return nextSlide
}
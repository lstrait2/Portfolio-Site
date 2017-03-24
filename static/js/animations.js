$(document).ready(function(){
        $(".img-responsive").hover(
            function(){
                $(this).animate({
                    opacity: '0.5'

                });
            },
            function(){
                $(this).animate({
                    opacity: '1.0'

                });
            }
        );
        $(".col-md-5").hover(
            function(){
                $("p").animate({
                    fontSize: '20px'

                });
                $("h3").animate({
                    fontSize: '48px'

                });
            },
            function(){
                $("p").animate({
                    fontSize: '10px'

                });
                $("h3").animate({
                    fontSize: '24px'

                });
            }
        );

        $
});
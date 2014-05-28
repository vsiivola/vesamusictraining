/*jslint browser: true*/
/*globals Translator, lang, $*/

var et = new Translator("exercisepage", lang);

function Choice(type, image, ogg, mp3, text) {
    "use strict";
    this.type = type;
    this.image = image;
    this.ogg = ogg;
    this.mp3 = mp3;
    this.text = text;

    this.build_dom = function () {
        if (this.type === "image_question" || this.type === "image_response") {
            this.dom = $('<td align="center" width="260"><img src="' +
                         this.image + '"></img><br>' + this.text + '</td>');
            return;
        }

        var empty_stave_td = $('<td align="center" width="260"><img src="/static/generated_assets/images/empty_stave.png" class="empty_image"></img></td>');

        if (this.type === "audio_question") {
            this.dom = empty_stave_td;
            return;
        }

        this.dom = $('<td align="center" width="260"><table class="buttontable"><tr class="empty_stave"></tr><tr><td align="center"><button class="ui-button-text">' + et.tp("Play") + '</button></td></tr></table>');
        $("tr.empty_stave", this.dom).append(empty_stave_td);
    };

    this.play_audio = function () {
        var audioElement = document.createElement('audio'),
            source = document.createElement('source');

        if (audioElement.canPlayType('audio/ogg;')) {
            source.type = 'audio/ogg';
            source.src = this.ogg;
        } else {
            source.type = 'audio/mpeg';
            source.src = this.mp3;
        }
        audioElement.appendChild(source);
        audioElement.play();
    };

    this.initial_overlays = function () {
        var img = $("img", this.dom),
            span_icon = $('<span class="span_icon"></span>'),
            overlay_context = this;

        setTimeout(function () {
            span_icon.css("top", img.offset().top + "px");
            span_icon.css("left", img.offset().left - 2 + "px");
            overlay_context.dom.append(span_icon);

            if (overlay_context.type === "audio_question"
                    || overlay_context.type === "audio_response") {

                var span_qmark = $('<span class="qmark altaudio">?</span>');
                span_qmark.css("top", img.offset().top + "px");
                span_qmark.css("left", img.offset().left + 60 + "px");
                overlay_context.dom.append(span_qmark);
                $(".empty_image", overlay_context).delay(500).animate({opacity: 0.2}, 3000);
                span_qmark.delay(200).animate({opacity: 1.0}, 3000);

                if (overlay_context.type === "audio_question") {
                    setTimeout(function () {
                        span_icon.addClass("ui-icon ui-icon-circle-triangle-e");
                    }, 200);
                    overlay_context.dom.click(function () {
                        overlay_context.play_audio();
                    });
                }
            }
        }, 2000);
    };

    this.display_result = function (myex, parent, correct) {
        var span_icon = $("span.span_icon", this.dom),
            img = $("img", this.dom),
            color,
            mydom,
            topobj;

        if (correct) {
            span_icon.addClass("ui-icon ui-icon-circle-check checkremove");
            color = "rgb(100,200,100)";
        } else {
            span_icon.addClass("ui-icon ui-icon-circle-close checkremove");
            color = "rgb(200,100,100)";
            if (this.type === "image_response") {
                this.play_audio();
            }
        }

        if (this.type === "audio_response") {
            img.attr("src", this.image);
            $(".empty_image", this.dom).animate({opacity: 0.8}, 3000);

            mydom = this.dom;
            topobj = this;
            img.load(function () {
                var span_qmark = $("span.qmark", mydom);
                span_icon.css("top", $(this).offset().top + "px");
                span_icon.css("left", $(this).offset().left - 2 + "px");
                span_qmark.css("top", $(this).offset().top + "px");
                span_qmark.css("left", $(this).offset().left + 60 + "px");
                span_qmark.animate({opacity: 0.0}, 3000);

                topobj.do_overlay(myex, parent, mydom, img, color, span_icon, correct);
            });
        } else {
            this.do_overlay(myex, parent, this.dom, img, color, span_icon, correct);
        }
    };

    this.do_overlay = function (ex, parenta, mydom, img, color, span_icon, correct) {
        var overlay = $('<div class="overlay"></div>');
        overlay.width(img.css("width"));
        overlay.height(img.css("height"));
        overlay.css("top", img.offset().top + "px");
        overlay.css("left", img.offset().left + "px");
        overlay.css("background-color", color);
        overlay.css("opacity", "0.7");
        mydom.append(overlay);
        span_icon.animate({opacity: 1.0}, 3000);

        //$("div#debug").append("exnum " + ex.mainWindow.exercise_index)
        parenta.dom.ready(function () {
            $("div", parenta.dom).animate(
                {opacity: 0.2},
                {duration: 1500, easing: 'linear', complete: function () {
                    if (correct) {
                        if (ex.num_clicks === 1) {
                            ex.mainWindow.correct_clicks += 1;
                        }
                        ex.mainWindow.exercise_index += 1;
                        ex.clear_statics(function () {
                            ex.mainWindow.show.apply(ex.mainWindow);
                        });
                        return;
                    }
                }}
            );
        });
    };

    this.bind_events = function (ethis) {
        var event_context = this,
            clickable = null;
        if (this.type === "audio_response") {
            $("button", this.dom).click(function () {
                event_context.play_audio();
            });
            clickable = $(".empty_stave, .altaudio", this.dom);
        } else {
            clickable = this.dom;
        }

        clickable.one("click", function () {
            $(".empty_stave, .altaudio", event_context).off("click");
            ethis.num_clicks += 1;
            //$("div#debug").append("cidx " + athis.idstring + ", img" + athis.image);
            $.get('/exercise/' + ethis.mainWindow.course_name + '/verify/',
                {
                    "exercise_index" : ethis.mainWindow.exercise_index,
                    "chosen" : event_context.type === "audio_response" ?
                            event_context.ogg : event_context.image,
                    "num_exercises" : ethis.mainWindow.num_exercises
                },
                function (response) {
                    var respi = JSON.parse(response);
                    event_context.image = respi.image;
                    event_context.mp3 = respi.mp3;
                    event_context.ogg = respi.ogg;
                    event_context.text = respi.text;
                    //$("div#debug").append("cidx " + athis.idstring + ", img" + athis.image);
                    event_context.display_result(ethis, event_context, respi.correct);
                });
        });
    };
}

function ExerciseScreen(mainWindow) {
    "use strict";
    this.mainWindow = mainWindow;

    this.render_full = function (response) {
        var escreen_context = this,
            escreen_args = arguments;
        $("div#main").slideUp("slow", function () {
            escreen_context.real_render.apply(escreen_context, escreen_args);
        });
    };

    this.real_render = function (response) {
        this.mainWindow.num_exercises = response.num_exercises;
        $("#maintitle").html(et.tp("Music Training") + " | " + this.mainWindow.course_name);
        var tstring = (
            '<h2 class="ui-widget-header ui-corner-all" style="text-align:center;">' +
                response.name +
                " (" + (this.mainWindow.exercise_index + 1) +
                "/" + (this.mainWindow.num_exercises)
                + ')</h2>\
<div class="ui-widget-content" id="test_images">\
 <table width="100%" cellpadding="20%">\
  <tr id="question"></tr></table>\
 <table width="100%" class="alttable">\
  <tr id="alttr"></tr>\
 </table>\
</div>'),
            q,
            render_context,
            i,
            c;

        $("div#main").html(tstring);

        q = new Choice(
            response.question_type + "_question",
            response.question_image,
            response.question_ogg,
            response.question_mp3,
            response.text
        );
        q.build_dom();
        $("tr#question").append(q.dom);

        render_context = this;
        this.choices = [];
        for (i = 0; i < response.num_alt; i += 1) {
            if (response.question_type === "audio") {
                c = new Choice(
                    "image_response",
                    response["alt" + i + "_image"],
                    null,
                    null,
                    response["alt" + i + "_text"]
                );
            } else {
                c = new Choice(
                    "audio_response",
                    null,
                    response["alt" + i + "_ogg"],
                    response["alt" + i + "_mp3"],
                    response["alt" + i + "_text"]
                );
            }
            c.build_dom();
            $("tr#alttr").append(c.dom);
            this.choices[i] = c;
        }

        this.num_clicks = 0;
        $("div#main").slideDown(function () {
            q.play_audio();
            q.initial_overlays();
            for (i = 0; i < response.num_alt; i += 1) {
                render_context.choices[i].initial_overlays();
                render_context.choices[i].bind_events(render_context);
            }
        });
    };

    this.get_server_info = function (course_name, exercise_index) {
        var that = this; //preserve context for callback
        //$("div#debug").append(" getting exnum " + exercise_index)
        $.get(
            '/exercise/' + course_name + '/lecture/',
            {"exercise_index": exercise_index},
            function (response) {that.res.apply(that, arguments); }
        );
    };

    this.res = function (response) {
        this.render_full(JSON.parse(response));
    };

    this.clear_statics = function (callback) {
        $("span").removeClass("ui-icon ui-icon-circle-triangle-e ui-icon-circle-check ui-icon-circle-close checkremove");
        $("div.overlay").css("opacity", "0.0");
        $("span.qmark").css("opacity", "0.0");
        callback();
    };
}

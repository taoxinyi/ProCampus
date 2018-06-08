function load_protobuf() {
        protobuf.load("{% static "notification_message.proto" %}", function (err, root) {
            if (err)
                throw err;
            var notification = root.lookupType("chat.Notification");
            var notificationItem = root.lookupType("chat.NotificationItem");

            var selected_array = Array();
            var add_array = Array();
            $("#my-tags-for-the-person").children(".tag-item").each(function () {
                selected_array.push($(this).children(":first").html());
            });
            $("#dialog_popup").click(function () {
                $(".tag-add-dialog").show();
            });
            $(".tag-dialog-close").click(function () {
                $(".tag-add-dialog").hide();
            });
            $("#dialog-diy").click(function () {
                $("#tag-dialog-input-div").show();
            });
            $("#tag-diy-cancel").click(function () {
                $("#tag-dialog-input-div").hide();
            });
            $("#tag-diy-submit").click(function () {
                var input_tag = $(".tag-dialog-input").val();
                if (selected_array.includes(input_tag)) alert("该标签已经存在！");
                else {
                    selected_array.push(input_tag);
                    add_array.push(input_tag);
                    $("#my-tags-for-the-person").append("<span class=\"tag-item\"><span>" +
                        input_tag + "</span><span class=\"tag-delete\">x</span></span>"
                    );
                    $("#my-tags-for-the-person").children(":last").children(":last").click(function () {
                        var deleted_tag = $(this).parent().children(":first").html();
                        var index = selected_array.indexOf(deleted_tag);
                        if (index !== -1) {
                            selected_array.splice(index, 1);
                        }
                        index = add_array.indexOf(deleted_tag);
                        if (index !== -1)
                            add_array.splice(index, 1);
                        else
                            add_array.push(deleted_tag);

                        $(this).parent().remove();
                    });
                    $(".tag-dialog-input").val("");
                }
            });
            $(".tag-dialog-save").click(function () {
                var input_tag = $(".tag-dialog-input").val();
                if (selected_array.includes(input_tag)) alert("该标签已经存在！");
                else {
                    var payload = {
                        type: 4,
                        fromClientId:{{ currentuser.id }},
                        toClientId:{{ theuser.id }},
                        tag: add_array
                    };
                    var item = notificationItem.create(payload);
                    var buffer = notificationItem.encode(item).finish();
                    FriendSocket.send(buffer);
                    location.reload();

                }
            });
            $(".tag-delete").click(function () {
                var deleted_tag = $(this).parent().children(":first").html();
                var index = selected_array.indexOf(deleted_tag);
                if (index !== -1) {
                    selected_array.splice(index, 1);
                }
                index = add_array.indexOf(deleted_tag);
                if (index !== -1)
                    add_array.splice(index, 1);
                else
                    add_array.push(deleted_tag);

                alert(add_array);
                $(this).parent().remove();

            });

            $("#button_comment").click(function () {
                $(".comment-add-dialog").show();
            });
            $(".comment-dialog-close").click(function () {
                $(".comment-add-dialog").hide();
            });
            $(".comment-dialog-save").click(function () {
                var m = editor.getContent({
                    emojiSign: '|', //表情分隔符
                    blockSign: '%' //行块分隔符
                });
                if (m === "") return;

                var payload = {
                    type: 5,
                    fromClientId:{{ currentuser.id }},
                    toClientId:{{ theuser.id }},
                    text: delete_br(m),
                    isPublic: $('#checkbox-is-public').is(":checked"),
                    isAnonymous: $('#checkbox-is-anonymous').is(":checked")
                };
                var item = notificationItem.create(payload);
                var buffer = notificationItem.encode(item).finish();
                FriendSocket.send(buffer);
                location.reload();
            });

            var comment_objects_list = {{ comment_list |safe}};
            for (i = 0; i < comment_objects_list.length; i++) {
                //alert(JSON.stringify(comment_objects_list[i]));
                var comment_index = comment_objects_list[i].pk;
                var original_like_count = comment_objects_list[i].like_user_count;
                var original_dislike_count = comment_objects_list[i].dislike_user_count;
                var like_span = $("<span>" + original_like_count + "</span>");
                var dislike_span = $("<span>" + original_dislike_count + "</span>");
                var right_div = $('<div style="display:flex"></div>');
                var helpful_div = $('<div style="display:flex;margin-right:10px"></div>');
                var not_helpful_div = $('<div style="display:flex"></div>');

                var helpful_img = $('<i class="fas fa-thumbs-up"></i>\n');

                var not_helpful_img = $('<i class="fas fa-thumbs-down"></i>\n');
                if (comment_objects_list[i].is_like) helpful_img.css('color', 'black');
                else if (comment_objects_list[i].is_dislike) not_helpful_img.css('color', 'black');
                helpful_img.click([comment_index, not_helpful_img, original_like_count, original_dislike_count], function (l) {
                    $(this).css('color', 'black');
                    l.data[1].css('color', 'gray');
                    var id = l.data[0];
                    var payload = {
                        type: 6,
                        fromClientId:{{ currentuser.id }},
                        commentId: id
                    };
                    var item = notificationItem.create(payload);
                    var buffer = notificationItem.encode(item).finish();
                    FriendSocket.send(buffer);
                });
                not_helpful_img.click([comment_index, helpful_img, original_like_count, original_dislike_count], function (l) {
                    $(this).css('color', 'black');
                    l.data[1].css('color', 'gray');
                    var id = l.data[0];
                    var payload = {
                        type: 7,
                        fromClientId:{{ currentuser.id }},
                        commentId: id
                    };
                    var item = notificationItem.create(payload);
                    var buffer = notificationItem.encode(item).finish();
                    FriendSocket.send(buffer);
                });
                helpful_div.append(helpful_img);
                helpful_div.append(like_span);

                not_helpful_div.append(not_helpful_img);
                not_helpful_div.append(dislike_span);

                right_div.append(helpful_div);
                right_div.append(not_helpful_div);

                var comment_div = $('<div class="block-container" style="padding:20px;display:flex;align-items:center; justify-content: space-between"></div>');
                comment_div.html("<span>" + convertToHtml(comment_objects_list[i].text) + "</span>");

                comment_div.append(right_div);
                $("#comment_list").append(comment_div);
                //$("#comment_list").append("<div class=\"block-container\" style=\"padding:20px\">" + convertToHtml(comment_objects_list[i]["fields"].text) + "</div>");
            }

        });

    }
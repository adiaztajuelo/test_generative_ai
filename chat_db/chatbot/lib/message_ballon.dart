import 'package:chatbot/chat_model.dart';
import 'package:flutter/material.dart';

class MessageBallon extends StatelessWidget {

  final Message message;

  const MessageBallon({super.key, required this.message});

  @override
  Widget build(BuildContext context) {

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
      child: Row(
        mainAxisAlignment: message.from == Chatter.assistant ? MainAxisAlignment.start : MainAxisAlignment.end,
        children: [
          Flexible(
            child: Container(
              decoration: BoxDecoration(
                color: message.from == Chatter.user ? Colors.blue
                  : message.from == Chatter.system ? Colors.orange[200]
                  : message.from == Chatter.assistant && message.to == Chatter.user ? Colors.grey[300]
                  : Colors.yellow[400],
                borderRadius: BorderRadius.circular(16)
              ),
              margin: const EdgeInsets.only(left: 50),
              padding: const EdgeInsets.all(8.0),
              child: Text(
                message.content,
                style: TextStyle(color: message.from == Chatter.user ? Colors.white : Colors.black)
              )
            )
          )
        ]
      )
    );
  }
}
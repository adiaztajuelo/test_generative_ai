import 'package:flutter/material.dart';

class InputMessage extends StatefulWidget {

  final void Function(String) sendMessage;

  const InputMessage({super.key, required this.sendMessage});

  @override
  State<InputMessage> createState() => _InputMessageState();
}

class _InputMessageState extends State<InputMessage> {

  final TextEditingController _messageController = TextEditingController();
  final FocusNode _inputFocusNode = FocusNode();

  void sendMessage() {
    if (_messageController.text.isNotEmpty) {
      widget.sendMessage(_messageController.text);
      if (mounted) setState(() => _messageController.clear());
    }
    _inputFocusNode.requestFocus();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(8.0),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _messageController,
              focusNode: _inputFocusNode,
              keyboardType: TextInputType.multiline,
              minLines: 1,
              maxLines: 4,
              maxLength: 4000,
              buildCounter: (BuildContext context, {required int currentLength, required int? maxLength, required bool isFocused}) => null,
              decoration: InputDecoration(
                hintText: 'Escribe un mensaje...',
                fillColor: Colors.white,
                filled: true,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(32.0),
                  borderSide: BorderSide.none
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(32.0),
                  borderSide: BorderSide.none
                )
              ),
              onSubmitted: (_) => sendMessage()
            )
          ),
          IconButton(
            icon: const Icon(Icons.send),
            onPressed: sendMessage
          )
        ]
      )
    );
  }
}
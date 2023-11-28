import 'dart:async';
import 'dart:convert';

import 'package:chatbot/chat_model.dart';
import 'package:chatbot/input_message.dart';
import 'package:chatbot/message_ballon.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class ChatHome extends StatefulWidget {

  const ChatHome({super.key});

  @override
  State<ChatHome> createState() => _ChatHomeState();
}

class _ChatHomeState extends State<ChatHome> {

  Future<dynamic> fetchData(String queryLink) async {
    return jsonDecode((await http.get(Uri.parse(queryLink))).body);
  }

  void loadChat() {
    fetchData('http://localhost:5000/load_chat').then((result) => setState(() =>
      messages = List<Map<String, dynamic>>.from(result).map(Message.fromDict).toList().reversed.toList()
    ));
  }

  List<Message> messages = [];
  late Timer timer;
  @override
  void initState() {
    timer = Timer.periodic(const Duration(seconds: 1), (timer) => loadChat());
    super.initState();
  }

  void sendMessage(String content) {
    fetchData('http://localhost:5000/send_message?message=$content');
  }

  void startChat() {
    fetchData('http://localhost:5000/new_chat');
    setState(() => chatInitialized = true);
  }
  
  bool chatInitialized = false;
  bool hideDeep = true;
  @override
  Widget build(BuildContext context) {

    List<Message> messagesToShow = messages;
    if (hideDeep) {
      messagesToShow = messages.where((message) => message.from == Chatter.user || message.to == Chatter.user).toList();
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('GenAI ChatBot'),
        actions: [
          Switch(
            value: !hideDeep, onChanged: (value) => setState(() => hideDeep = !value)
          )
        ]
      ),
      body: chatInitialized ? Column(
        children: [
          Expanded(
            child: ListView.builder(
              reverse: true,
              itemCount: messagesToShow.length,
              itemBuilder: (context, index) => MessageBallon(
                message: messagesToShow[index]
              )
            )
          ),
          InputMessage(sendMessage: sendMessage)
        ]
      ) : Center(child: ElevatedButton(onPressed: startChat, child: const Text('Iniciar chat')))
    );
  }

  @override
  void dispose() {
    timer.cancel();
    super.dispose();
  }
}
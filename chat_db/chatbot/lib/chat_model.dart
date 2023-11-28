
class Message {

  final Chatter from;
  final Chatter to;
  final String content;

  Message({required this.from, required this.to, required this.content});

  factory Message.fromDict(Map<String, dynamic> data) {
    return Message(
      content: data['content'],
      from: Chatter.values.where((chatter) => chatter.name == data['from']).first,
      to: Chatter.values.where((chatter) => chatter.name == data['to']).first
    );
  }
}

enum Chatter {
  user,
  assistant,
  system
}

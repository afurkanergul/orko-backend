from app.services.parser import RegexCommandParser

if __name__ == "__main__":
    parser = RegexCommandParser()
    cmd = parser.parse("sell 500 tons of corn to client X", context={"channel": "cli"})
    print(cmd.to_dict())

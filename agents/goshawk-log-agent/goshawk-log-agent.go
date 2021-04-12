// 
// Goshawk AMQP Log Sender
// @version 0.1
// 

package main

import (
  "os"
  "log"
  "fmt"
  "github.com/akamensky/argparse"
  "github.com/hpcloud/tail"
  "github.com/streadway/amqp"
  "github.com/ilyakaznacheev/cleanenv"
)

func rmqFailOnError(err error, msg string) {
  if err != nil {
    log.Fatalf("%s: %s", msg, err)
  }
}

func parseConfigFile(file string) (*Config, error) {
	var cfg Config

	err := cleanenv.ReadConfig(file, &cfg)
  if err != nil {
    log.Printf("Error reading configuration from file:%v", file)
    return nil, err
  }

	return &cfg, nil
}

type Config struct {
  Rabbitmq struct {
    Host string `yaml:"host"`
    Port string `yaml:"port"`
    Proto string `yaml:"proto"`
    Vhost string `yaml:"vhost"`
    User string `yaml:"user"`
    Pass string `yaml:"pass"`
    Exchange string `yaml:"exchange"`
  } `yaml:"rabbitmq"`
  Logfile string `yaml:"logfile"`
}

func main() {
  parser := argparse.NewParser(
    "goshawk-log-agent",
    "\rGoshawk AMQP Log Sender\nVersion: 0.1")
  
  configfile := parser.String(
    "c",
    "config-file",
    &argparse.Options{
      Required: false,
      Help: "Config file"})
  
  verbose := parser.Flag(
    "v",
    "verbose",
    &argparse.Options{
      Required: false,
      Help: "Verbose output, print logs"})

  err := parser.Parse(os.Args)

  if err != nil {
		fmt.Print(parser.Usage(err))
    os.Exit(1)
	}
  
	hostname, err := os.Hostname()
	if err != nil {
		panic(err)
	}

  cfg, err := parseConfigFile(*configfile)

  uri := "" + cfg.Rabbitmq.Proto + "://" +
    cfg.Rabbitmq.User + ":" + cfg.Rabbitmq.Pass + "@" +
    cfg.Rabbitmq.Host + ":" + string(cfg.Rabbitmq.Port) + "/" +
    cfg.Rabbitmq.Vhost

    fmt.Println("AMQP URI", uri)
    fmt.Println("Routing key:", hostname)
    fmt.Println("Logfile", cfg.Logfile)

  conn, err := amqp.Dial(uri)
  rmqFailOnError(err, "Failed to connect to RabbitMQ")
  defer conn.Close()

  ch, err := conn.Channel()
  rmqFailOnError(err, "Failed to open a channel")
  defer ch.Close()

  t, err := tail.TailFile(
    cfg.Logfile,
    tail.Config{
      Follow: true,
      ReOpen: true,
      MustExist: true,
      Location: &tail.SeekInfo{0, os.SEEK_END}})

  if err != nil {
    fmt.Println("MustExist:true is violated")
    t.Stop()
  }

  for line := range t.Lines {
    if (*verbose) {
      fmt.Println(line.Text)
    }
    
    err = ch.Publish(
      cfg.Rabbitmq.Exchange, // exchange
      hostname,              // routing key
      false,                 // mandatory
      false,                 // immediate
      amqp.Publishing {
        ContentType: "text/plain",
        Body:        []byte(line.Text),
      })

  }

}


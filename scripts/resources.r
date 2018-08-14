library(ggplot2)

if(file.exists("output/cpu_stats.csv")){
	df <- read.csv("output/cpu_stats.csv", sep=",", header=T)

    p <- ggplot(df) + theme_bw()
    p <- p + geom_line(aes(x=time, y=cpu_usage))
    p <- p + theme(legend.position="bottom", legend.direction="horizontal") + xlab("Time into experiment (sec)") + ylab("CPU usage (%)")
    p

    ggsave(file="output/cpu_history.png", width=8, height=6, dpi=100)
}

if(file.exists("output/memory_stats.csv")){
	df <- read.csv("output/memory_stats.csv", sep=",", header=T)
    df$memory_usage = df$memory_usage / 1024 / 1024

    p <- ggplot(df) + theme_bw()
    p <- p + geom_line(aes(x=time, y=memory_usage))
    p <- p + theme(legend.position="bottom", legend.direction="horizontal") + xlab("Time into experiment (sec)") + ylab("Memory usage (MB)")
    p

    ggsave(file="output/memory_history.png", width=8, height=6, dpi=100)
}

library(ggplot2)

if(file.exists("output/cpu_stats.csv")){
	df <- read.csv("output/cpu_stats.csv", sep=",", header=T)

    p <- ggplot(df) + theme_bw()
    p <- p + geom_line(aes(x=time, y=cpu_usage))
    p <- p + theme(legend.position="bottom", legend.direction="horizontal")
    p

    ggsave(file="output/cpu_history.png", width=8, height=6, dpi=100)
}

if(file.exists("output/memory_stats.csv")){
	df <- read.csv("output/memory_stats.csv", sep=",", header=T)

    p <- ggplot(df) + theme_bw()
    p <- p + geom_line(aes(x=time, y=memory_usage))
    p <- p + theme(legend.position="bottom", legend.direction="horizontal")
    p

    ggsave(file="output/memory_history.png", width=8, height=6, dpi=100)
}

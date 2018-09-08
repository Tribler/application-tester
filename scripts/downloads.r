library(ggplot2)

if(file.exists("output/download_stats.csv")){
	df <- read.csv("output/download_stats.csv", sep=",", header=T)
	df$speed_up = df$speed_up / 1024
	df$speed_down = df$speed_down / 1024
    df$dl_progress = df$progress * 100

    # Speed up
    p <- ggplot(df) + theme_bw()
    p <- p + geom_line(aes(x=time, y=speed_up, group=infohash, colour=infohash))
    p <- p + theme(legend.position="bottom", legend.direction="horizontal") + xlab("Time into experiment (sec)") + ylab("Upload speed (kb/s)")
    p

    ggsave(file="output/speed_up.png", width=8, height=6, dpi=100)

    # Speed down
    p <- ggplot(df) + theme_bw()
    p <- p + geom_line(aes(x=time, y=speed_down, group=infohash, colour=infohash))
    p <- p + theme(legend.position="bottom", legend.direction="horizontal") + xlab("Time into experiment (sec)") + ylab("Download speed (kb/s)")
    p

    ggsave(file="output/speed_down.png", width=8, height=6, dpi=100)

    # Progress
    p <- ggplot(df) + theme_bw()
    p <- p + geom_line(aes(x=time, y=dl_progress, group=dl_progress, colour=dl_progress))
    p <- p + theme(legend.position="bottom", legend.direction="horizontal") + xlab("Time into experiment (sec)") + ylab("Progress (%)")
    p

    ggsave(file="output/progress.png", width=8, height=6, dpi=100)
}

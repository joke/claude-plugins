package task.scheduler;

import java.time.Instant;

public final class ScheduledTask implements Comparable<ScheduledTask> {

    private final String name;
    private final int priority;
    private final Instant scheduledTime;
    private final Runnable action;

    public ScheduledTask(final String name, final int priority, final Instant scheduledTime, final Runnable action) {
        this.name = name;
        this.priority = priority;
        this.scheduledTime = scheduledTime;
        this.action = action;
    }

    public String getName() {
        return name;
    }

    public int getPriority() {
        return priority;
    }

    public Instant getScheduledTime() {
        return scheduledTime;
    }

    public Runnable getAction() {
        return action;
    }

    @Override
    public int compareTo(final ScheduledTask other) {
        return Integer.compare(other.priority, this.priority);
    }

    @Override
    public String toString() {
        return "ScheduledTask{name='" + name + "', priority=" + priority + ", scheduledTime=" + scheduledTime + "}";
    }
}

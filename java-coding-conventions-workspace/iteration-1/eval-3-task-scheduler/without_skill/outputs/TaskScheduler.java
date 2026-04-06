package task.scheduler;

import java.time.Instant;
import java.util.Optional;
import java.util.PriorityQueue;
import java.util.Queue;

public final class TaskScheduler {

    private final Queue<ScheduledTask> taskQueue;

    public TaskScheduler() {
        this.taskQueue = new PriorityQueue<>();
    }

    public void schedule(final ScheduledTask task) {
        taskQueue.add(task);
    }

    public void schedule(final String name, final int priority, final Instant scheduledTime, final Runnable action) {
        final ScheduledTask task = new ScheduledTask(name, priority, scheduledTime, action);
        schedule(task);
    }

    public Optional<ScheduledTask> getNextTask() {
        return Optional.ofNullable(taskQueue.poll());
    }

    public int countPendingTasks() {
        return taskQueue.size();
    }

    public boolean hasPendingTasks() {
        return !taskQueue.isEmpty();
    }
}

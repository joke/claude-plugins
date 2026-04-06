import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.PriorityQueue;

public class TaskScheduler {

    private final PriorityQueue<ScheduledTask> pendingTasks;

    public TaskScheduler() {
        this.pendingTasks = new PriorityQueue<>();
    }

    public void schedule(final ScheduledTask task) {
        pendingTasks.add(task);
    }

    public ScheduledTask getNextTask() {
        final ScheduledTask task = pendingTasks.poll();
        if (task == null) {
            throw new NoTaskAvailableException();
        }
        return task;
    }

    public int countPendingTasks() {
        return pendingTasks.size();
    }

    public boolean hasPendingTasks() {
        return !pendingTasks.isEmpty();
    }

    public List<ScheduledTask> drainByPriority() {
        final List<ScheduledTask> drained = new ArrayList<>();
        while (hasPendingTasks()) {
            drained.add(pendingTasks.poll());
        }
        return Collections.unmodifiableList(drained);
    }
}

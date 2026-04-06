public class NoTaskAvailableException extends RuntimeException {

    public NoTaskAvailableException() {
        super("No tasks available in the scheduler");
    }
}

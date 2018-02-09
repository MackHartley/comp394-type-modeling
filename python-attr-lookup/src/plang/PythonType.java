package plang;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * A Python class.
 */
public class PythonType extends PythonObject {

    private final String name;
    private final PythonObject base;

    /**
     * Declares a new Python type. Equivalent to Python `class «name»(«base»):`
     * @param name The name of this class.
     * @param base The base class of this class. May be null.
     *             (In real Python, instead of null it would be the class called `object`, and
     *             it would be a list instead of a single value.)
     */
    public PythonType(String name, PythonObject base) {
        super(null);  // In real Python, this would be the type called `type`
        this.name = name;
        this.base = base;
    }

    /**
     * The name of this class.
     */
    public String getName() {
        return name;
    }

    /**
     * The base type (superclass) of this class.
     */
    public PythonObject getBase() {
        return base;
    }

    @Override
    protected List<PythonObject> buildMRO() {

        List<PythonObject> result = new ArrayList<>();
        result.add(this);
        if(this.base != null) {
            result.addAll(this.base.buildMRO());
        }
        return result;

    }

    /**
     * Creates and returns a new instance of this class, i.e. a PythonObject whose type is
     * this PythonType.
     */
    public PythonObject instantiate() {

        if(name != null && !name.equals("")) {
            return new PythonObject(this);
        }

        throw new UnsupportedOperationException("PyObject name cannot be null");
    }

    @Override
    public String toString() {
        return "PythonType<" + name + ">";
    }
}

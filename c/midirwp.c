#include <Python.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <alsa/asoundlib.h>

static PyObject *AlsaError;

#define RAISE(message) \
    { PyErr_SetString(AlsaError, message); return NULL; }


static snd_seq_t *seq;

static int my_client_id; /* this program */
static int dest_client_id; /* the midi device */

static int readable_port;
static int writable_port;

static snd_seq_event_t ev;
static snd_seq_event_t *in_event;

static int err;


static PyObject *setup(PyObject *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, "i", &dest_client_id))
        return NULL;

    // open client
    err = snd_seq_open(&seq, "default", SND_SEQ_OPEN_DUPLEX, 0);
    if (err < 0)
        RAISE("couldnt open sequencer connection\n");
    
    // get client id
    my_client_id = snd_seq_client_id(seq);

    // create readable port for sending events
    readable_port = snd_seq_create_simple_port(
                                               seq, "my readable port",
                                               SND_SEQ_PORT_CAP_READ | SND_SEQ_PORT_CAP_SUBS_READ,
                                               SND_SEQ_PORT_TYPE_MIDI_GENERIC);

    // create writable port for receiving events
    writable_port = snd_seq_create_simple_port(
                                               seq, "my writable port",
                                               SND_SEQ_PORT_CAP_WRITE | SND_SEQ_PORT_CAP_SUBS_WRITE,
                                               SND_SEQ_PORT_TYPE_MIDI_GENERIC);

    // make subscription for sending events to device
    if (snd_seq_connect_to(seq, readable_port, dest_client_id, 0) < 0)
        RAISE("Unable to subscribe to MIDI port for writing.\n");

    // make subscription for capturing events from midi device
    if (snd_seq_connect_from(seq, writable_port, dest_client_id, 0) < 0)
        RAISE("Unable to subscribe to MIDI port for reading.\n");

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *teardown(PyObject *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, "")) /* no args */
        return NULL;
    
    // exit gracefully
    snd_seq_disconnect_to(seq, readable_port, dest_client_id, 0);
    snd_seq_disconnect_from(seq, writable_port, dest_client_id, 0);
    snd_seq_close(seq);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *get_event(PyObject *self, PyObject *args) 
{
    if (!PyArg_ParseTuple(args, "")) /* no args */
        return NULL;
    
    Py_BEGIN_ALLOW_THREADS
    err = snd_seq_event_input(seq, &in_event);
    Py_END_ALLOW_THREADS
    
    if (err < 0)
        return NULL;

    if (in_event->type == SND_SEQ_EVENT_NOTEON || 
        in_event->type == SND_SEQ_EVENT_NOTEOFF)
    {
        return Py_BuildValue("iiii",
                             in_event->type,
                             in_event->data.note.channel,
                             in_event->data.note.note,
                             in_event->data.note.velocity);
    }
    else if (in_event->type == SND_SEQ_EVENT_CONTROLLER) 
    {
        return Py_BuildValue("iiii",
                             in_event->type,
                             in_event->data.control.channel,
                             in_event->data.control.param,
                             in_event->data.control.value);
    }


    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *get_event_nb(PyObject *self, PyObject *args) 
{
    if (!PyArg_ParseTuple(args, "")) /* no args */
        return NULL;
    
    int n_events = snd_seq_event_input_pending(seq, 1);
    if (n_events > 0)
        return get_event(self, args);

    Py_INCREF(Py_None);
    return Py_None;
}

static void send()
{
    snd_seq_ev_set_source(&ev, readable_port);
    snd_seq_ev_set_dest(&ev, dest_client_id, 0);
    snd_seq_ev_set_direct(&ev);
        
    snd_seq_event_output(seq, &ev);
    snd_seq_drain_output(seq);
}


static PyObject *send_note_on(PyObject *self, PyObject *args)
{
    int channel, note, velocity;
    
    if (!PyArg_ParseTuple(args, "iii", &channel, &note, &velocity))
        return NULL;
    
    snd_seq_ev_clear(&ev);
    snd_seq_ev_set_noteon(&ev, channel, note, velocity);
    send();

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *send_control_change(PyObject *self, PyObject *args)
{
    int channel, param, value;
    
    if (!PyArg_ParseTuple(args, "iii", &channel, &param, &value))
        return NULL;
    
    snd_seq_ev_clear(&ev);
    snd_seq_ev_set_controller(&ev, channel, param, value);
    send();

    Py_INCREF(Py_None);
    return Py_None;
}

static struct PyMethodDef alsa_methods[] =
{
    {"setup", setup, 1},
    {"get_event", get_event, 1},
    {"get_event_nb", get_event_nb, 1},
    {"send_note_on", send_note_on, 1},
    {"send_control_change", send_control_change, 1},
    {"close", teardown, 1},
    {NULL, NULL}
};

void initmidirwp()
{
    PyObject *m;

    m = Py_InitModule("midirwp", alsa_methods);

    AlsaError = PyErr_NewException("midirwp.error", NULL, NULL);
    Py_INCREF(AlsaError);
    PyModule_AddObject(m, "error", AlsaError);

    if (PyErr_Occurred())
        Py_FatalError("Unable to initialize module midirwp.");
}

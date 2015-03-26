# Authors: Daniel Strohmeier <daniel.strohmeier@tu-ilmenau.de>
#
# License: BSD (3-clause)

import os.path as op

import numpy as np
from numpy.testing import assert_array_almost_equal
from nose.tools import assert_true

from mne.io import Raw
from mne.io.pick import pick_types
from mne.event import read_events
from mne.epochs import Epochs
from ..stim import fix_stim_artifact_raw, fix_stim_artifact

data_path = op.join(op.dirname(__file__), '..', '..', 'io', 'tests', 'data')
raw_fname = op.join(data_path, 'test_raw.fif')
event_fname = op.join(data_path, 'test-eve.fif')


def test_stim_fix_raw():
    """Test eliminate stim artifact"""
    raw = Raw(raw_fname, preload=True)
    events = read_events(event_fname)
    event_idx = np.where(events[:, 2] == 1)[0][0]
    tidx = int(events[event_idx, 0] - raw.first_samp)

    # use window around stimulus
    tmin, tmax = -0.02, 0.02
    test_tminidx = int(-0.01 * raw.info['sfreq'])
    test_tmaxidx = int(0.01 * raw.info['sfreq'])

    raw = fix_stim_artifact_raw(raw, events, event_id=1, tmin=tmin,
                                  tmax=tmax, mode='linear')
    data, times = raw[:, (tidx + test_tminidx):(tidx + test_tmaxidx)]
    diff_data0 = np.diff(data[0])
    diff_data0 -= np.mean(diff_data0)
    assert_array_almost_equal(diff_data0, np.zeros(len(diff_data0)))
    raw = fix_stim_artifact_raw(raw, events, event_id=1, tmin=tmin,
                                  tmax=tmax, mode='window')
    data, times = raw[:, (tidx + test_tminidx):(tidx + test_tmaxidx)]
    assert_true(np.all(data) == 0.)

    # use window before stimulus
    tmin, tmax= -0.045, 0.015
    test_tminidx = int(-0.035 * raw.info['sfreq'])
    test_tmaxidx = int(-0.015 * raw.info['sfreq'])

    raw = fix_stim_artifact_raw(raw, events, event_id=1, tmin=tmin,
                                  tmax=tmax, mode='linear')
    data, times = raw[:, (tidx + test_tminidx):(tidx + test_tmaxidx)]
    diff_data0 = np.diff(data[0])
    diff_data0 -= np.mean(diff_data0)
    assert_array_almost_equal(diff_data0, np.zeros(len(diff_data0)))
    raw = fix_stim_artifact_raw(raw, events, event_id=1, tmin=tmin,
                                  tmax=tmax, mode='window')
    data, times = raw[:, (tidx + test_tminidx):(tidx + test_tmaxidx)]
    assert_true(np.all(data) == 0.)

    # use window after stimulus
    tmin, tmax = 0.005, 0.045
    test_tminidx = int(0.015 * raw.info['sfreq'])
    test_tmaxidx = int(0.035 * raw.info['sfreq'])

    raw = fix_stim_artifact_raw(raw, events, event_id=1, tmin=tmin,
                                  tmax=tmax, mode='linear')
    data, times = raw[:, (tidx + test_tminidx):(tidx + test_tmaxidx)]
    diff_data0 = np.diff(data[0])
    diff_data0 -= np.mean(diff_data0)
    assert_array_almost_equal(diff_data0, np.zeros(len(diff_data0)))
    raw = fix_stim_artifact_raw(raw, events, event_id=1, tmin=tmin,
                                  tmax=tmax, mode='window')
    data, times = raw[:, (tidx + test_tminidx):(tidx + test_tmaxidx)]
    assert_true(np.all(data) == 0.)


def test_stim_fix_evoked():
    """Test eliminate stim artifact"""
    raw = Raw(raw_fname, preload=True)
    events = read_events(event_fname)
    tmin, tmax, event_id = -0.2, 0.5, 1
    picks = pick_types(raw.info, meg=True, eeg=True,
                       eog=True, stim=False, exclude='bads')
    epochs = Epochs(raw, events, event_id, tmin, tmax,
                    picks=picks, preload=False)

    # use window before stimulus
    evoked = epochs.average()
    tmin, tmax= -0.2, 0.1
    test_tminidx = int(-0.1 * evoked.info['sfreq']) - evoked.first
    test_tmaxidx = int(0.05 * evoked.info['sfreq']) - evoked.first
    evoked = fix_stim_artifact(evoked, tmin, tmax, mode='window')
    data = evoked.data[:, test_tminidx:test_tmaxidx]
    assert_true(np.all(data) == 0.)

    # use window after stimulus
    tmin, tmax= 0.2, 0.4
    test_tminidx = int(0.25 * evoked.info['sfreq']) - evoked.first
    test_tmaxidx = int(0.35 * evoked.info['sfreq']) - evoked.first
    evoked = fix_stim_artifact(evoked, tmin, tmax, mode='window')
    data = evoked.data[:, test_tminidx:test_tmaxidx]
    assert_true(np.all(data) == 0.)


def test_stim_fix_epochs():
    """Test eliminate stim artifact"""
    raw = Raw(raw_fname, preload=True)
    events = read_events(event_fname)
    tmin, tmax, event_id = -0.2, 0.5, 1
    picks = pick_types(raw.info, meg=True, eeg=True,
                       eog=True, stim=False, exclude='bads')
    epochs = Epochs(raw, events, event_id, tmin, tmax,
                    picks=picks, preload=True)
    e_start = int(np.ceil(epochs.info['sfreq'] * epochs.tmin))

    # use window before stimulus
    tmin, tmax= -0.15, 0.1
    test_tminidx = int(-0.1 * epochs.info['sfreq']) - e_start
    test_tmaxidx = int(0.05 * epochs.info['sfreq']) - e_start
    epochs = fix_stim_artifact(epochs, tmin, tmax, mode='window')
    data = epochs._data[:, test_tminidx:test_tmaxidx]
    assert_true(np.all(data) == 0.)

    # use window after stimulus
    tmin, tmax= 0.2, 0.4
    test_tminidx = int(0.25 * epochs.info['sfreq']) - e_start
    test_tmaxidx = int(0.35 * epochs.info['sfreq']) - e_start
    epochs = fix_stim_artifact(epochs, tmin, tmax, mode='window')
    data = epochs._data[:, test_tminidx:test_tmaxidx]
    assert_true(np.all(data) == 0.)

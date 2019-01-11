from astropy import units as u
import numpy as np
import warnings


# For definition of class ModelParameters see below.

# Different parameter sets. Any parameters that may be given as
# 'basic' should be a list. Parameters that may be 'optional' should
# be a list of length 2. The second item will only be printed if the
# effect is included in the 'optional' list (see _get_effect_strings()).
_valid_parameters = {
    'point lens': ['t_0, u_0, t_E'],
    'point lens alt': 'alternate: t_eff may be substituted for u_0 or t_E',
    'binary lens': ['s, q, alpha'],
    'triple lens': ['s_21, s_31, q_21, q_31, psi, alpha'],
    'finite source': ['rho', '(for finite source effects)'],
    'finite source alt': 'alternate: t_star may be substituted for t_E or rho',
    'parallax': ['pi_E OR pi_E_N, pi_E_E', '(for parallax)'],
    'parallax opt': [
        't_0_par',
        'may also be specified for parallax models. Defaults to t_0.'],
    'lens orbital motion': ['dalpha_dt, ds_dt', '(for orbital motion)'],
    'lens orbital motion opt': [
        't_0_kep',
        'may also be specified for orbital motion models. Defaults to t_0.']}


def _get_effect_strings(*args):
    """
    Given *args[0], figure out which parameters should be printed.

    'basic' = fundamental parameters of the model or effect described
        by args[0]
    'additional' = any additional fundamental parameters (an extension
        of 'basic')
    'alternate' = possible substitutions for the fundamental parameters
    'optional' = parameters that may also be specified for the given
        model type.

    e.g. 'FSPL' returns basic = [t_0, u_0, tE], additional = [rho, s,
    q, alpha], alternate = [t_eff, t_star], and optional = [pi_E or
    pi_E_N, pi_E_E]
    """
    basic = None
    additional = []
    alternate = []
    optional = []

    args_0 = args[0].lower().replace(" ", "")

    # number of lenses
    if args_0 == 'pointlens' or args_0[2:4] == 'pl':
        basic = 'point lens'
        alternate.append('point lens alt')

    if args_0 == 'binarylens':
        basic = 'binary lens'

    if args_0[2:4] == 'bl':
        basic = 'point lens'
        additional.append('binary lens')
        alternate.append('point lens alt')

    # Effects
    if args_0 == 'finitesource':
        basic = 'finite source'
        alternate.append('finite source alt')

    if args_0[0:2] == 'fs':
        additional.append('finite source')
        alternate.append('finite source alt')

    if args_0 == 'parallax':
        basic = 'parallax'
        optional.append('parallax opt')

    if len(args[0]) == 4:
        optional.append('parallax')
        optional.append('parallax opt')

    if args[0].lower() == 'lens orbital motion':
        basic = 'lens orbital motion'
        optional.append('lens orbital motion opt')

    if len(args[0]) == 4 and args[0][2:4].lower() == 'bl':
        optional.append('lens orbital motion')
        optional.append('lens orbital motion opt')

    return {
        'basic': basic, 'additional': additional, 'alternate': alternate,
        'optional': optional}


def _print_parameters(header, components):
    """
    Prints the given parameter information under the requested header.

    Arguments:
        header: *str*

        components: *dictionary*
            This should be created using _get_effect_strings()
    """
    print(header)
    if components['basic'] is not None:
        parameters_list = 'basic: {0}'.format(
            _valid_parameters[components['basic']][0])
        if len(components['additional']) > 0:
            for item in components['additional']:
                parameters_list += ', {0}'.format(_valid_parameters[item][0])
        print('{0}'.format(parameters_list))

    if len(components['alternate']) > 0:
        for item in components['alternate']:
            print('{0}'.format(_valid_parameters[item]))

    if len(components['optional']) > 0:
        for item in components['optional']:
            print('optional: {0} {1}'.format(
                    _valid_parameters[item][0], _valid_parameters[item][1]))


def _print_all():
    """
    Give the user general information about common models and effects.
    """
    print('------------------------')
    print('Some common model types:')
    print('------------------------')
    _print_parameters('PSPL: ', _get_effect_strings('PSPL'))
    _print_parameters('----\nFSBL: ', _get_effect_strings('FSBL'))
    print('-----------------')
    print('Optional Effects:')
    print('-----------------')
    _print_parameters('finite source: ', _get_effect_strings('finite source'))
    _print_parameters('---------\nparallax: ', _get_effect_strings('parallax'))
    _print_parameters(
        '---------\nlens orbital motion: ',
        _get_effect_strings('lens orbital motion'))
    print('-----------------')
    print('All Options: (call using which_parameters([option]) )')
    print('-----------------')
    print("Model types: 'PSPL', 'FSPL', 'PSBL', 'FSBL'")
    print("Effects: 'point lens', 'binary lens', 'finite source', " +
          "'parallax', 'lens orbital motion'")


def which_parameters(*args):
    """
    Prints information on valid parameter combinations that can be
    used to define a model or a particular effect. May be called with
    no arguments (returns information on many types of models) or with
    one argument referring to a specific model (e.g. PSPL) or effect
    (e.g. parallax).

    Valid arguments: *str*
        Model types: 'PSPL', 'FSPL', 'PSBL', 'FSBL'

        Effects: 'point lens', 'binary lens', 'finite source',
        'parallax', 'lens orbital motion'
    """
    if len(args) == 0:
        _print_all()
    else:
        components = _get_effect_strings(*args)
        header = '---------\n{0} parameters:'.format(args[0])
        _print_parameters(header, components)


class ModelParameters(object):
    """
    A class for the basic microlensing model parameters (t_0, u_0,
    t_E, rho, s, q, alpha, pi_E_E etc.). Can handle point lens or binary
    lens. The pi_E assumes NE coordinates (Parallel, Perpendicular
    coordinates are not supported).

    Arguments :
        parameters: *dictionary*
            A dictionary of parameters and their values. See
            :py:func:`which_parameters()` for valid parameter combinations.

    Attributes :
        parameters: *dictionary*
            A dictionary of parameters and their values. Do not use it to
            change paramter values, instead use e.g.:
            ``model_parameters.u_0 = 0.1`` or
            ``setattr(model_parameters, 'u_0', 0.1)``.

    Example:
        Define a point lens model:
            ``params = ModelParameters({'t_0': 2450000., 'u_0': 0.3,
            't_E': 35.})``

        Then you can print the parameters:
            ``print(params)``

    """
    def __init__(self, parameters):
        if not isinstance(parameters, dict):
            raise TypeError(
                'ModelParameters must be initialized with dict ' +
                "as a parameter\ne.g., ModelParameters({'t_0': " +
                "2456789.0, 'u_0': 0.123, 't_E': 23.45})")

        self._count_sources(parameters.keys())

        if self.n_sources == 1:
            self._check_valid_combination_1_source(parameters.keys())
        elif self.n_sources == 2:
            self._check_valid_combination_2_sources(parameters.keys())
            if 't_E' not in parameters.keys():
                raise KeyError('Currently, the binary source calculations ' +
                               'require t_E to be directly defined')
            (params_1, params_2) = self._divide_parameters(parameters)
            self._source_1_parameters = ModelParameters(params_1)
            self._source_2_parameters = ModelParameters(params_2)
            # This way we force checks from "== 1" above to be run on
            # each source paramteres separately.
        else:
            raise ValueError('wrong number of sources')
        self._set_parameters(parameters)

    def _count_sources(self, keys):
        """How many sources there are?"""
        binary_params = ['t_0_1', 't_0_2', 'u_0_1', 'u_0_2', 'rho_1', 'rho_2',
                         't_star_1', 't_star_2']
        if len(set(binary_params).intersection(set(keys))) > 0:
            self._n_sources = 2
        else:
            self._n_sources = 1

    def _divide_parameters(self, parameters):
        """
        Divide an input dict into 2 - each source separately.
        Some of the parameters are copied to both dicts.
        """
        separate_parameters = ['t_0_1', 't_0_2', 'u_0_1', 'u_0_2',
                               'rho_1', 'rho_2', 't_star_1', 't_star_2']
        parameters_1 = {}
        parameters_2 = {}
        for (key, value) in parameters.items():
            if key in separate_parameters:
                if key[-2:] == "_1":
                    parameters_1[key[:-2]] = value
                elif key[-2:] == "_2":
                    parameters_2[key[:-2]] = value
                else:
                    raise ValueError('unexpected error')
            else:
                parameters_1[key] = value
                parameters_2[key] = value
        return (parameters_1, parameters_2)

    def __repr__(self):
        """A nice way to represent a ModelParameters object as a string"""

        keys = set(self.parameters.keys())
        if 'pi_E' in keys:
            keys.remove('pi_E')
            keys |= {'pi_E_E', 'pi_E_N'}

        # Below we define dict of dicts. Key of inner ones: 'width',
        # 'precision', and optional: 'unit' and 'name'.
        formats = {
            't_0': {'width': 13, 'precision': 5, 'unit': 'HJD'},
            'u_0': {'width': 9, 'precision': 6},
            't_eff': {'width': 10, 'precision': 6, 'unit': 'd'},
            't_E': {'width': 10, 'precision': 4, 'unit': 'd'},
            'rho': {'width': 7, 'precision': 5},
            't_star': {'width': 13, 'precision': 6, 'unit': 'd'},
            'pi_E_N': {'width': 9, 'precision': 5},
            'pi_E_E': {'width': 9, 'precision': 5},
            's': {'width': 9, 'precision': 5},
            'q': {'width': 12, 'precision': 8},
            'alpha': {'width': 11, 'precision': 5, 'unit': 'deg'},
            'ds_dt': {
                'width': 11, 'precision': 5, 'unit': '/yr', 'name': 'ds/dt'},
            'dalpha_dt': {
                'width': 18, 'precision': 5, 'unit': 'deg/yr',
                'name': 'dalpha/dt'},
            # Values below are just guesses:
            's_21': {'width': 9, 'precision': 5},
            's_31': {'width': 9, 'precision': 5},
            'q_21': {'width': 12, 'precision': 8},
            'q_31': {'width': 12, 'precision': 8},
            'psi': {'width': 11, 'precision': 5, 'unit': 'deg'}
            # end of guessed values.
        }
        # Add binary source parameters with the same settings.
        binary_source_keys = ['t_0_1', 't_0_2', 'u_0_1', 'u_0_2',
                              'rho_1', 'rho_2', 't_star_1', 't_star_2']
        for key in binary_source_keys:
            form = formats[key[:-2]]
            formats[key] = {'width': form['width'],
                            'precision': form['precision']}
            if 'unit' in form:
                formats[key]['unit'] = form['unit']
            if 'name' in form:
                raise KeyError('internal issue: {:}'.format(key))
        formats_keys = [
            't_0', 't_0_1', 't_0_2', 'u_0', 'u_0_1', 'u_0_2', 't_eff', 't_E',
            'rho', 'rho_1', 'rho_2', 't_star', 't_star_1', 't_star_2',
            'pi_E_N', 'pi_E_E', 's', 'q', 'alpha', 'ds_dt', 'dalpha_dt',
            's_21', 's_31', 'q_21', 'q_31', 'psi'
        ]

        variables = ''
        values = ''

        for key in formats_keys:
            if key not in keys:
                continue
            form = formats[key]
            fmt_1 = '{:>' + str(form['width'])
            fmt_2 = fmt_1 + '.' + str(form['precision']) + 'f} '
            fmt_1 += '} '
            full_name = form.get('name', key)
            if 'unit' in form:
                full_name += " ({:})".format(form['unit'])
            variables += fmt_1.format(full_name)
            value = getattr(self, key)
            if isinstance(value, u.Quantity):
                value = value.value
            values += fmt_2.format(value)

        return '{0}\n{1}\n'.format(variables, values)

    def _check_valid_combination_2_sources(self, keys):
        """
        make sure that there is no conflict between t_0 and t_0_1 etc.
        """
        binary_params = ['t_0_1', 't_0_2', 'u_0_1', 'u_0_2', 'rho_1', 'rho_2',
                         't_star_1', 't_star_2']
        for parameter in binary_params:
            if parameter in keys:
                if parameter[:-2] in keys:
                    raise ValueError('You cannot set {:} and {:}'.format(
                                        parameter, parameter[:-2]))

    def _check_valid_combination_1_source(self, keys):
        """
        Check that the user hasn't over-defined the ModelParameters.
        """
        raise NotImplementedError('NOT YET IMPLEMENTED FOR TRIPLE LENS')
        # Make sure that there are no unwanted keys
        allowed_keys = set([
            't_0', 'u_0', 't_E', 't_eff', 's', 'q', 'alpha', 'rho', 't_star',
            'pi_E', 'pi_E_N', 'pi_E_E', 't_0_par', 'dalpha_dt', 'ds_dt',
            's_21', 's_31', 'q_21', 'q_31', 'psi',
            't_0_kep', 't_0_1', 't_0_2', 'u_0_1', 'u_0_2', 'rho_1', 'rho_2',
            't_star_1', 't_star_2'])
        difference = set(keys) - allowed_keys
        if len(difference) > 0:
            derived_1 = ['gamma', 'gamma_perp', 'gamma_parallel']
            if set(keys).intersection(derived_1):
                msg = ('You cannot set gamma, gamma_perp, ' +
                       'or gamma_parallel. These are derived parameters. ' +
                       'You can set ds_dt and dalpha_dt instead.\n')
            else:
                msg = ""
            msg += 'Unrecognized parameters: {:}'.format(difference)
            raise KeyError(msg)

        # Make sure that mimum set of parameters are defined - we need to know
        # t_0, u_0, and t_E.
        if 't_0' not in keys:
            raise KeyError('t_0 must be defined')
        if ('u_0' not in keys) and ('t_eff' not in keys):
            raise KeyError('not enough information to calculate u_0')
        if (('t_E' not in keys) and
                (('u_0' not in keys) or ('t_eff' not in keys)) and
                (('rho' not in keys) or ('t_star' not in keys))):
            raise KeyError('not enough information to calculate t_E')

        # If s, q, and alpha must all be defined if one is defined
        if ('s' in keys) or ('q' in keys) or ('alpha' in keys):
            if ('s' not in keys) or ('q' not in keys) or ('alpha' not in keys):
                raise KeyError(
                    'A binary model requires all three of (s, q, alpha).')

        # Cannot define all 3 parameters for 2 observables
        if ('t_E' in keys) and ('rho' in keys) and ('t_star' in keys):
            raise KeyError('Only 1 or 2 of (t_E, rho, t_star) may be defined.')

        if ('t_E' in keys) and ('u_0' in keys) and ('t_eff' in keys):
            raise KeyError('Only 1 or 2 of (u_0, t_E, t_eff) may be defined.')

        # Cannot define t_E in 2 different ways
        if (('rho' in keys) and ('t_star' in keys) and ('u_0' in keys) and
                ('t_eff' in keys)):
            raise KeyError('You cannot define rho, t_star, u_0, and t_eff')

        # Parallax is either pi_E or (pi_E_N, pi_E_E)
        if 'pi_E' in keys and ('pi_E_N' in keys or 'pi_E_E' in keys):
            raise KeyError(
                'Parallax may be defined EITHER by pi_E OR by ' +
                '(pi_E_N and pi_E_E).')

        # If parallax is defined, then both components must be set:
        if ('pi_E_N' in keys) != ('pi_E_E' in keys):
            raise KeyError(
                'You have to define either both or none of (pi_E_N, pi_E_E).')

        # t_0_par makes sense only when parallax is defined.
        if 't_0_par' in keys:
            if 'pi_E' not in keys and 'pi_E_N' not in keys:
                raise KeyError(
                    't_0_par makes sense only when parallax is defined.')

        # Parallax needs reference epoch:
        if 'pi_E' in keys or 'pi_E_N' in keys:
            if 't_0' not in keys and 't_0_par' not in keys:
                raise KeyError(
                    'Parallax is defined, hence either t_0 or t_0_par has ' +
                    'to be set.')

        # If ds_dt is defined, dalpha_dt must be defined
        if ('ds_dt' in keys) or ('dalpha_dt' in keys):
            if ('ds_dt' not in keys) or ('dalpha_dt' not in keys):
                raise KeyError(
                    'Lens orbital motion requires both ds_dt and dalpha_dt.' +
                    '\nNote that you can set either of them to 0.')
        # If orbital motion is defined, then we need binary lens.
            if (
                    ('s' not in keys) or ('q' not in keys) or
                    ('alpha' not in keys)):
                raise KeyError(
                    'Lens orbital motion requires >2 bodies (s, q, alpha).')
        # If orbital motion is defined, then reference epoch has to be set.
            if 't_0' not in keys and 't_0_kep' not in keys:
                raise KeyError(
                    'Orbital motion requires reference epoch, ' +
                    'i.e., t_0 or t_0_kep')

        # t_0_kep makes sense only when orbital motion is defined.
        if 't_0_kep' in keys:
            if 'ds_dt' not in keys or 'dalpha_dt' not in keys:
                raise KeyError(
                    't_0_kep makes sense only when orbital motion is defined.')

    def _check_valid_parameter_values(self, parameters):
        """
        Prevent user from setting negative (unphysical) values for
        t_E, t_star, rho.
        """
        names = ['t_E', 't_star', 'rho']
        full_names = {
            't_E': 'Einstein timescale',
            't_star': 'Source crossing time', 'rho': 'Source size'}

        for name in names:
            if name in parameters.keys():
                if parameters[name] < 0.:
                    raise ValueError("{:} cannot be negative: {:}".format(
                            full_names[name], parameters[name]))

    def _set_parameters(self, parameters):
        """
        check if patameter values make sense and remember the copy of the dict
        """
        self._check_valid_parameter_values(parameters)
        self.parameters = dict(parameters)

    def _update_sources(self, parameter, value):
        """
        For multi-source models, update the values for all sources.
        Note that pi_E_N and pi_E_E are changed separately.
        """
        if self.n_sources == 1:
            return

        if parameter in self._source_1_parameters.parameters:
            setattr(self._source_1_parameters, parameter, value)
        if parameter in self._source_2_parameters.parameters:
            setattr(self._source_2_parameters, parameter, value)

    @property
    def t_0(self):
        """
        *float*

        The time of minimum projected separation between the source
        and the lens center of mass.
        """
        return self.parameters['t_0']

    @t_0.setter
    def t_0(self, new_t_0):
        self.parameters['t_0'] = new_t_0
        self._update_sources('t_0', new_t_0)

    @property
    def u_0(self):
        """
        *float*

        The minimum projected separation between the source
        and the lens center of mass.
        """
        if 'u_0' in self.parameters.keys():
            return self.parameters['u_0']
        else:
            try:
                return self.parameters['t_eff'] / self.parameters['t_E']
            except KeyError:
                raise AttributeError(
                    'u_0 is not defined for these parameters: {0}'.format(
                        self.parameters.keys()))

    @u_0.setter
    def u_0(self, new_u_0):
        if 'u_0' in self.parameters.keys():
            self.parameters['u_0'] = new_u_0
            self._update_sources('u_0', new_u_0)
        else:
            raise KeyError('u_0 is not a parameter of this model.')

    @property
    def t_star(self):
        """
        *float*

        t_star = rho * t_E = source radius crossing time

        "day" is the default unit. Can be set as *float* or
        *astropy.Quantity*, but always returns *float* in units of days.
        """
        if 't_star' in self.parameters.keys():
            self._check_time_quantity('t_star')
            return self.parameters['t_star'].to(u.day).value
        else:
            try:
                return (self.parameters['t_E'].to(u.day).value *
                        self.parameters['rho'])
            except KeyError:
                raise AttributeError(
                    't_star is not defined for these parameters: {0}'.format(
                        self.parameters.keys()))

    @t_star.setter
    def t_star(self, new_t_star):
        if 't_star' in self.parameters.keys():
            self._set_time_quantity('t_star', new_t_star)
            self._update_sources('t_star', new_t_star)
        else:
            raise KeyError('t_star is not a parameter of this model.')

        if new_t_star < 0.:
            raise ValueError(
                'Source crossing time cannot be negative:', new_t_star)

    @property
    def t_eff(self):
        """
        *float*

        t_eff = u_0 * t_E = effective timescale

        "day" is the default unit. Can be set as *float* or
        *astropy.Quantity*, but always returns *float* in units of days.
        """
        if 't_eff' in self.parameters.keys():
            self._check_time_quantity('t_eff')
            return self.parameters['t_eff'].to(u.day).value
        else:
            try:
                return (self.parameters['t_E'].to(u.day).value *
                        self.parameters['u_0'])
            except KeyError:
                raise AttributeError(
                    't_eff is not defined for these parameters: {0}'.format(
                        self.parameters.keys()))

    @t_eff.setter
    def t_eff(self, new_t_eff):
        if 't_eff' in self.parameters.keys():
            self._set_time_quantity('t_eff', new_t_eff)
            self._update_sources('t_eff', new_t_eff)
        else:
            raise KeyError('t_eff is not a parameter of this model.')

    @property
    def t_E(self):
        """
        *float*

        The Einstein timescale. "day" is the default unit. Can be set as
        *float* or *astropy.Quantity*, but always returns *float* in units of
        days.
        """
        if 't_E' in self.parameters.keys():
            self._check_time_quantity('t_E')
            return self.parameters['t_E'].to(u.day).value
        elif ('t_star' in self.parameters.keys() and
              'rho' in self.parameters.keys()):
            return self.t_star/self.rho
        elif ('t_eff' in self.parameters.keys() and
              'u_0' in self.parameters.keys()):
            return self.t_eff/self.u_0
        else:
            raise KeyError("You're trying to access t_E that was not set")

    @t_E.setter
    def t_E(self, new_t_E):
        if new_t_E is None:
            raise ValueError('Must provide a value')

        if new_t_E < 0.:
            raise ValueError('Einstein timescale cannot be negative:', new_t_E)

        if 't_E' in self.parameters.keys():
            self._set_time_quantity('t_E', new_t_E)
            self._update_sources('t_E', new_t_E)
        else:
            raise KeyError('t_E is not a parameter of this model.')

    def _set_time_quantity(self, key, new_time):
        """
        Save a variable with units of time (e.g. t_E, t_star,
        t_eff). If units are not given, assume days.
        """
        if isinstance(new_time, u.Quantity):
            self.parameters[key] = new_time
        else:
            self.parameters[key] = new_time * u.day

    def _check_time_quantity(self, key):
        """
        Make sure that value for give key has quantity, add it if missing.
        """
        if not isinstance(self.parameters[key], u.Quantity):
            self._set_time_quantity(key, self.parameters[key])

    @property
    def rho(self):
        """
        *float*

        source size as a fraction of the Einstein radius
        """
        if 'rho' in self.parameters.keys():
            return self.parameters['rho']
        elif ('t_star' in self.parameters.keys() and
              't_E' in self.parameters.keys()):
            return self.t_star/self.t_E
        else:
            return None

    @rho.setter
    def rho(self, new_rho):
        if 'rho' in self.parameters.keys():
            if new_rho < 0.:
                raise ValueError('source size (rho) cannot be negative')
            self.parameters['rho'] = new_rho
            self._update_sources('rho', new_rho)
        else:
            raise KeyError('rho is not a parameter of this model.')

    @property
    def alpha(self):
        """
        *astropy.Quantity*

        The angle of the source trajectory relative to the binary lens
        axis (or primary-secondary axis). Measured counterclockwise,
        i.e., according to convention advocated by `Skowron et
        al. 2011 (ApJ, 738, 87)
        <http://adsabs.harvard.edu/abs/2011ApJ...738...87S>`_.  May be
        set as a *float* --> assumes "deg" is the default unit.
        Regardless of input value, returns value in degrees.
        """
        if not isinstance(self.parameters['alpha'], u.Quantity):
            self.parameters['alpha'] = self.parameters['alpha'] * u.deg

        return self.parameters['alpha'].to(u.deg)

    @alpha.setter
    def alpha(self, new_alpha):
        if isinstance(new_alpha, u.Quantity):
            self.parameters['alpha'] = new_alpha
        else:
            self.parameters['alpha'] = new_alpha * u.deg
        self._update_sources('alpha', new_alpha)

    @property
    def q(self):
        """
        *float*

        mass ratio of the two lens components. Only 2 bodies allowed.
        """
        if isinstance(self.parameters['q'], (list, np.ndarray)):
            self.parameters['q'] = self.parameters['q'][0]
        return self.parameters['q']

    @q.setter
    def q(self, new_q):
        self.parameters['q'] = new_q
        self._update_sources('q', new_q)

    @property
    def s(self):
        """
        *float*

        separation of the two lens components relative to Einstein ring size
        """
        if isinstance(self.parameters['s'], (list, np.ndarray)):
            self.parameters['s'] = self.parameters['s'][0]
        return self.parameters['s']

    @s.setter
    def s(self, new_s):
        if new_s < 0.:
            raise ValueError(
                'Binary lens separation cannot be negative:', new_s)

        self.parameters['s'] = new_s
        self._update_sources('s', new_s)

    @property
    def s_21(self):
        raise NotImplementedError('triple lens parameters')

    @s_21.setter
    def s_21(self, new_s_21):
        raise NotImplementedError('triple lens parameters')

    @property
    def s_31(self):
        raise NotImplementedError('triple lens parameters')

    @s_31.setter
    def s_31(self, new_s_31):
        raise NotImplementedError('triple lens parameters')

    @property
    def q_21(self):
        raise NotImplementedError('triple lens parameters')

    @q_21.setter
    def q_21(self, new_q_21):
        raise NotImplementedError('triple lens parameters')

    @property
    def q_31(self):
        raise NotImplementedError('triple lens parameters')

    @q_31.setter
    def q_31(self, new_q_31):
        raise NotImplementedError('triple lens parameters')

    @property
    def psi(self):
        raise NotImplementedError('triple lens parameters')

    @psi.setter
    def psi(self, new_psi):
        raise NotImplementedError('triple lens parameters')

    @property
    def pi_E(self):
        """
        *list of floats*

        The microlensing parallax vector. Must be set as a vector/list
        (i.e. [pi_E_N, pi_E_E]). To get the magnitude of pi_E, use
        pi_E_mag
        """
        if 'pi_E' in self.parameters.keys():
            return self.parameters['pi_E']
        elif ('pi_E_N' in self.parameters.keys() and
              'pi_E_E' in self.parameters.keys()):
            return [self.parameters['pi_E_N'], self.parameters['pi_E_E']]
        else:
            return None

    @pi_E.setter
    def pi_E(self, new_pi_E):
        if isinstance(new_pi_E, np.ndarray):
            new_pi_E = new_pi_E.flatten()

        if 'pi_E' in self.parameters.keys():
            if len(new_pi_E) == 2:
                self.parameters['pi_E'] = new_pi_E
                self._update_sources('pi_E', new_pi_E)
            else:
                raise TypeError('pi_E is a 2D vector. It must have length 2.')

        elif ('pi_E_N' in self.parameters.keys() and
              'pi_E_E' in self.parameters.keys()):
            self.parameters['pi_E_N'] = new_pi_E[0]
            self.parameters['pi_E_E'] = new_pi_E[1]
            self._update_sources('pi_E_N', new_pi_E[0])
            self._update_sources('pi_E_E', new_pi_E[1])
        else:
            raise KeyError('pi_E is not a parameter of this model.')

    @property
    def pi_E_N(self):
        """
        *float*

        The North component of the microlensing parallax vector.
        """
        if 'pi_E_N' in self.parameters.keys():
            return self.parameters['pi_E_N']
        elif 'pi_E' in self.parameters.keys():
            return self.parameters['pi_E'][0]
        else:
            raise KeyError('pi_E_N not defined for this model')

    @pi_E_N.setter
    def pi_E_N(self, new_value):
        if 'pi_E_N' in self.parameters.keys():
            self.parameters['pi_E_N'] = new_value
            self._update_sources('pi_E_N', new_value)
        elif 'pi_E' in self.parameters.keys():
            self.parameters['pi_E'][0] = new_value
            if self.n_sources != 1:
                self._source_1_parameters.parameters['pi_E'][0] = new_value
                self._source_2_parameters.parameters['pi_E'][0] = new_value
        else:
            raise KeyError('pi_E_N is not a parameter of this model.')

    @property
    def pi_E_E(self):
        """
        *float*

        The East component of the microlensing parallax vector.
        """
        if 'pi_E_E' in self.parameters.keys():
            return self.parameters['pi_E_E']
        elif 'pi_E' in self.parameters.keys():
            return self.parameters['pi_E'][1]
        else:
            raise KeyError('pi_E_N not defined for this model')

    @pi_E_E.setter
    def pi_E_E(self, new_value):
        if 'pi_E_E' in self.parameters.keys():
            self.parameters['pi_E_E'] = new_value
            self._update_sources('pi_E_E', new_value)
        elif 'pi_E' in self.parameters.keys():
            self.parameters['pi_E'][1] = new_value
            if self.n_sources != 1:
                self._source_1_parameters.parameters['pi_E'][1] = new_value
                self._source_2_parameters.parameters['pi_E'][1] = new_value
        else:
            raise KeyError('pi_E_E is not a parameter of this model.')

    @property
    def t_0_par(self):
        """
        *float*

        The reference time for the calculation of parallax. If not set
        explicitly, set t_0_par = t_0.
        """
        if 't_0_par' not in self.parameters.keys():
            return self.parameters['t_0']
        else:
            return self.parameters['t_0_par']

    @t_0_par.setter
    def t_0_par(self, new_t_0_par):
        self.parameters['t_0_par'] = new_t_0_par
        self._update_sources('t_0_par', new_t_0_par)

    @property
    def pi_E_mag(self):
        """
        *float*

        The magnitude of the microlensing parallax vector.
        """
        if 'pi_E' in self.parameters.keys():
            pi_E_N = self.parameters['pi_E'][0]
            pi_E_E = self.parameters['pi_E'][1]
        elif ('pi_E_N' in self.parameters.keys() and
              'pi_E_E' in self.parameters.keys()):
            pi_E_N = self.parameters['pi_E_N']
            pi_E_E = self.parameters['pi_E_E']
        else:
            raise KeyError('pi_E not defined for this model')
        return np.sqrt(pi_E_N**2 + pi_E_E**2)

    @property
    def ds_dt(self):
        """
        *astropy.Quantity*

        Change rate of separation :py:attr:`~s` in 1/year. Can be set as
        *AstroPy.Quantity* or as *float* (1/year is assumed default unit).
        Regardless of input value, returns value in 1/year.
        """
        if not isinstance(self.parameters['ds_dt'], u.Quantity):
            self.parameters['ds_dt'] = self.parameters['ds_dt'] / u.yr

        return self.parameters['ds_dt'].to(1 / u.yr)

    @ds_dt.setter
    def ds_dt(self, new_ds_dt):
        if isinstance(new_ds_dt, u.Quantity):
            self.parameters['ds_dt'] = new_ds_dt
        else:
            self.parameters['ds_dt'] = new_ds_dt / u.yr
        self._update_sources('ds_dt', new_ds_dt)

    @property
    def dalpha_dt(self):
        """
        *astropy.Quantity*

        Change rate of angle :py:attr:`~alpha` in deg/year. Can be set as
        *AstroPy.Quantity* or as *float* (deg/year is assumed default unit).
        Regardless of input value, returns value in deg/year.
        """
        if not isinstance(self.parameters['dalpha_dt'], u.Quantity):
            self.parameters['dalpha_dt'] = (self.parameters['dalpha_dt'] *
                                            u.deg / u.yr)

        return self.parameters['dalpha_dt'].to(u.deg / u.yr)

    @dalpha_dt.setter
    def dalpha_dt(self, new_dalpha_dt):
        if isinstance(new_dalpha_dt, u.Quantity):
            self.parameters['dalpha_dt'] = new_dalpha_dt
        else:
            self.parameters['dalpha_dt'] = new_dalpha_dt * u.deg / u.yr
        self._update_sources('dalpha_dt', new_dalpha_dt)

    @property
    def t_0_kep(self):
        """
        *float*

        The reference time for the calculation of lens orbital motion.
        If not set explicitly, assumes t_0_kep = t_0.
        """
        if 't_0_kep' not in self.parameters.keys():
            return self.parameters['t_0']
        else:
            return self.parameters['t_0_kep']

    @t_0_kep.setter
    def t_0_kep(self, new):
        self.parameters['t_0_kep'] = new
        self._update_sources('t_0_kep', new)

    @property
    def t_0_1(self):
        """
        *float*

        The time of minimum projected separation between the source no. 1
        and the lens center of mass.
        """
        return self.parameters['t_0_1']

    @t_0_1.setter
    def t_0_1(self, new_t_0_1):
        self.parameters['t_0_1'] = new_t_0_1
        self._source_1_parameters.t_0 = new_t_0_1

    @property
    def t_0_2(self):
        """
        *float*

        The time of minimum projected separation between the source no. 2
        and the lens center of mass.
        """
        return self.parameters['t_0_2']

    @t_0_2.setter
    def t_0_2(self, new_t_0_2):
        self.parameters['t_0_2'] = new_t_0_2
        self._source_2_parameters.t_0 = new_t_0_2

    @property
    def u_0_1(self):
        """
        *float*

        The minimum projected separation between the source no. 1
        and the lens center of mass.
        """
        if 'u_0_1' in self.parameters.keys():
            return self.parameters['u_0_1']
        else:
            try:
                t_eff = self._source_1_parameters.parameters['t_eff']
                t_E = self._source_1_parameters.parameters['t_E']
                return t_eff / t_E
            except KeyError:
                raise AttributeError(
                    'u_0_1 is not defined for these parameters: {0}'.format(
                        self.parameters.keys()))

    @u_0_1.setter
    def u_0_1(self, new_u_0_1):
        if 'u_0_1' in self.parameters.keys():
            self.parameters['u_0_1'] = new_u_0_1
            self._source_1_parameters.u_0 = new_u_0_1
        else:
            raise KeyError('u_0_1 is not a parameter of this model.')

    @property
    def u_0_2(self):
        """
        *float*

        The minimum projected separation between the source no. 2
        and the lens center of mass.
        """
        if 'u_0_2' in self.parameters.keys():
            return self.parameters['u_0_2']
        else:
            try:
                t_eff = self._source_2_parameters.parameters['t_eff']
                t_E = self._source_2_parameters.parameters['t_E']
                return t_eff / t_E
            except KeyError:
                raise AttributeError(
                    'u_0_2 is not defined for these parameters: {0}'.format(
                        self.parameters.keys()))

    @u_0_2.setter
    def u_0_2(self, new_u_0_2):
        if 'u_0_2' in self.parameters.keys():
            self.parameters['u_0_2'] = new_u_0_2
            self._source_2_parameters.u_0 = new_u_0_2
        else:
            raise KeyError('u_0_2 is not a parameter of this model.')

    @property
    def t_star_1(self):
        """
        *float*

        t_star_1 = rho_1 * t_E_1 = source no. 1 radius crossing time

        "day" is the default unit. Can be set as *float* or
        *astropy.Quantity*, but always returns *float* in units of days.
        """
        if 't_star_1' in self.parameters.keys():
            self._check_time_quantity('t_star_1')
            return self.parameters['t_star_1'].to(u.day).value
        else:
            try:
                t_E = self._source_1_parameters.parameters['t_E'].to(u.day)
                rho = self._source_1_parameters.parameters['rho']
                return t_E.value * rho
            except KeyError:
                raise AttributeError(
                    't_star_1 is not defined for these parameters: {0}'.format(
                        self.parameters.keys()))

    @t_star_1.setter
    def t_star_1(self, new_t_star_1):
        if 't_star_1' in self.parameters.keys():
            self._set_time_quantity('t_star_1', new_t_star_1)
            self._source_1_parameters.t_star = new_t_star_1
        else:
            raise KeyError('t_star_1 is not a parameter of this model.')

        if new_t_star_1 < 0.:
            raise ValueError(
                'Source crossing time cannot be negative:', new_t_star_1)

    @property
    def t_star_2(self):
        """
        *float*

        t_star_2 = rho_2 * t_E_2 = source no. 2 radius crossing time

        "day" is the default unit. Can be set as *float* or
        *astropy.Quantity*, but always returns *float* in units of days.
        """
        if 't_star_2' in self.parameters.keys():
            self._check_time_quantity('t_star_2')
            return self.parameters['t_star_2'].to(u.day).value
        else:
            try:
                t_E = self._source_2_parameters.parameters['t_E'].to(u.day)
                rho = self._source_2_parameters.parameters['rho']
                return t_E.value * rho
            except KeyError:
                raise AttributeError(
                    't_star_2 is not defined for these parameters: {0}'.format(
                        self.parameters.keys()))

    @t_star_2.setter
    def t_star_2(self, new_t_star_2):
        if 't_star_2' in self.parameters.keys():
            self._set_time_quantity('t_star_2', new_t_star_2)
            self._source_2_parameters.t_star = new_t_star_2
        else:
            raise KeyError('t_star_2 is not a parameter of this model.')

        if new_t_star_2 < 0.:
            raise ValueError(
                'Source crossing time cannot be negative:', new_t_star_2)

    @property
    def rho_1(self):
        """
        *float*

        source no. 1 size as a fraction of the Einstein radius
        """
        if 'rho_1' in self.parameters.keys():
            return self.parameters['rho_1']
        elif ('t_star' in self._source_1_parameters.parameters.keys() and
                't_E' in self._source_1_parameters.parameters.keys()):
            return (self._source_1_parameters.t_star /
                    self._source_1_parameters.t_E)
        else:
            return None

    @rho_1.setter
    def rho_1(self, new_rho_1):
        if 'rho_1' in self.parameters.keys():
            if new_rho_1 < 0.:
                raise ValueError('source size (rho_1) cannot be negative')
            self.parameters['rho_1'] = new_rho_1
            self._source_1_parameters.rho = new_rho_1
        else:
            raise KeyError('rho_1 is not a parameter of this model.')

    @property
    def rho_2(self):
        """
        *float*

        source no. 2 size as a fraction of the Einstein radius
        """
        if 'rho_2' in self.parameters.keys():
            return self.parameters['rho_2']
        elif ('t_star' in self._source_2_parameters.parameters.keys() and
                't_E' in self._source_2_parameters.parameters.keys()):
            return (self._source_2_parameters.t_star /
                    self._source_2_parameters.t_E)
        else:
            return None

    @rho_2.setter
    def rho_2(self, new_rho_2):
        if 'rho_2' in self.parameters.keys():
            if new_rho_2 < 0.:
                raise ValueError('source size (rho_2) cannot be negative')
            self.parameters['rho_2'] = new_rho_2
            self._source_2_parameters.rho = new_rho_2
        else:
            raise KeyError('rho_2 is not a parameter of this model.')

    def get_s(self, epoch):
        """
        Returns the value of separation :py:attr:`~s` at a given epoch or
        epochs (if orbital motion parameters are set).

        Arguments :
            epoch: *float*, *list*, *np.ndarray*
                The time(s) at which to calculate :py:attr:`~s`.

        Returns :
            separation: *float* or *np.ndarray*
                Value(s) of separation for given epochs.

        """
        if 'ds_dt' not in self.parameters.keys():
            return self.s

        if isinstance(epoch, list):
            epoch = np.array(epoch)

        s_of_t = (self.s + self.ds_dt * (epoch - self.t_0_kep) * u.d).value

        return s_of_t

    def get_alpha(self, epoch):
        """
        Returns the value of angle :py:attr:`~alpha` at a given epoch or
        epochs (if orbital motion parameters are set).

        Arguments :
            epoch: *float*, *list*, *np.ndarray*
                The time(s) at which to calculate :py:attr:`~alpha`.

        Returns :
            separation: *astropy.Quantity*
                Value(s) of angle for given epochs in degrees

        """
        if 'dalpha_dt' not in self.parameters.keys():
            return self.alpha

        if isinstance(epoch, list):
            epoch = np.array(epoch)

        alpha_of_t = (self.alpha + self.dalpha_dt * (epoch - self.t_0_kep)*u.d)

        return alpha_of_t.to(u.deg)

    @property
    def gamma_parallel(self):
        """
        *astropy.Quantity*

        Parallel component of instantaneous velocity of the secondary
        relative to the primary in 1/year.
        It is parallel to the primary-secondary axis.
        Equals :py:attr:`~ds_dt`/:py:attr:`~s`. Cannot be set.
        """
        return self.ds_dt / self.s

    @property
    def gamma_perp(self):
        """
        *astropy.Quantity*

        Perpendicular component of instantaneous velocity of the secondary
        relative to the primary. It is perpendicular to the primary-secondary
        axis. It has sign opposite to :py:attr:`~dalpha_dt`
        and is in rad/yr, not deg/yr. Cannot be set.
        """
        return -self.dalpha_dt.to(u.rad/u.yr)

    @property
    def gamma(self):
        """
        *astropy.Quantity*

        Instantaneous velocity of the secondary relative to the primary in
        1/year. Cannot be set.
        """
        gamma_perp = (self.gamma_perp / u.rad).to(1/u.yr)
        return (self.gamma_parallel**2 + gamma_perp**2)**0.5

    def is_static(self):
        """
        Checks if model is static, i.e., orbital motion parameters are not set.

        Returns :
            is_static: *boolean*
                *True* if *dalpha_dt* or *ds_dt* are set.

        """
        if ('dalpha_dt' in self.parameters.keys() or
                'ds_dt' in self.parameters.keys()):
            return False
        else:
            return True

    @property
    def n_lenses(self):
        """
        *int*

        number of objects in the lens system
        """
        if (('s' not in self.parameters.keys()) and
                ('q' not in self.parameters.keys()) and
                ('alpha' not in self.parameters.keys())):
            return 1
        else:
            return 2

    @property
    def n_sources(self):
        """
        *int*

        number of luminous sources; it's possible to be 1 for xallarap model
        """
        return self._n_sources

    @property
    def source_1_parameters(self):
        """
        :py:class:`~MulensModel.modelparameters.ModelParameters`

        Parameters of source 1 in multi-source model.

        **Do not change returned values.** To change
        parameters of the source 1, simply change the parameters of double
        source instance.
        """
        if self.n_sources == 1:
            raise ValueError('source_1_parameters cannot be accessed for ' +
                             'single source models')
        return self._source_1_parameters

    @property
    def source_2_parameters(self):
        """
        :py:class:`~MulensModel.modelparameters.ModelParameters`

        Parameters of source 2 in multi-source model.

        **Do not change returned values.** To change
        parameters of the source 1, simply change the parameters of double
        source instance.
        """
        if self.n_sources == 1:
            raise ValueError('source_2_parameters cannot be accessed for ' +
                             'single source models')
        return self._source_2_parameters

    def as_dict(self):
        """
        Give parameters as a dict.

        Returns :
            dictionary: *dict*
                The dictionary of model parameters.
        """
        return self.parameters

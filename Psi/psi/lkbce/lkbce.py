#!/usr/bin/python3

import fcntl
import multiprocessing
import os
import re
import shutil
import tarfile
import time
import urllib.parse

import psi.components
import psi.lkbce.cmds.cmds
import psi.utils

name = 'LKBCE'


class PsiComponentCallbacks(psi.components.PsiComponentCallbacksBase):
    pass


class PsiComponent(psi.components.PsiComponentBase):
    def launch(self):
        self.linux_kernel = {}
        self.fetch_linux_kernel_work_src_tree()
        self.make_canonical_linux_kernel_work_src_tree()
        self.clean_linux_kernel_work_src_tree()
        self.extract_linux_kernel_attrs()
        self.configure_linux_kernel()
        self.linux_kernel['raw build cmds file'] = 'Linux kernel raw build cmds'
        psi.components.launch_in_parrallel(self.logger,
                                           (self.build_linux_kernel, self.process_all_linux_kernel_raw_build_cmds))

    def build_linux_kernel(self):
        self.logger.info('Build Linux kernel')

        # First of all collect all build commands to be executed.
        cmds = []
        if 'whole build' in self.conf['Linux kernel']:
            cmds.append(('modules',))
        elif 'modules' in self.conf['Linux kernel']:
            # TODO: check that module sets aren't intersect explicitly.
            for modules in self.conf['Linux kernel']['modules']:
                if re.search(r'\.ko$', modules):
                    cmds.append((modules,))
                else:
                    # Add "modules_prepare" target once.
                    if cmds:
                        if cmds[0] != 'modules_prepare':
                            cmds.insert(0, 'modules_prepare')
                    cmds.append(('M={0}'.format(modules), 'modules'))
        else:
            raise KeyError(
                'Neither "whole build" nor "modules" attribute of Linux kernel is specified in configuration')

        for cmd in cmds:
            psi.components.Component(self.logger,
                                     tuple(['make', '-j',
                                            psi.utils.get_parallel_threads_num(self.logger,
                                                                               self.conf,
                                                                               'Linux kernel build'),
                                            '-C', self.linux_kernel['work src tree'],
                                            'ARCH={0}'.format(self.linux_kernel['arch'])] + list(cmd)),
                                     env=dict(os.environ,
                                              PATH='{0}:{1}'.format(os.path.join(os.path.dirname(__file__), 'cmds'),
                                                                    os.environ['PATH']),
                                              LINUX_KERNEL_RAW_BUILD_CMS_FILE=os.path.abspath(
                                                  self.linux_kernel['raw build cmds file']))).start()

        # Terminate Linux kernel raw build commands "message queue".
        with open(self.linux_kernel['raw build cmds file'], 'a') as fp:
            try:
                fcntl.flock(fp, fcntl.LOCK_EX)
                fp.write(psi.lkbce.cmds.cmds.Command.cmds_separator)
            finally:
                fcntl.flock(fp, fcntl.LOCK_UN)

    def clean_linux_kernel_work_src_tree(self):
        self.logger.info('Clean Linux kernel working source tree')
        psi.components.Component(self.logger, ('make', '-C', self.linux_kernel['work src tree'], 'mrproper')).start()

    def configure_linux_kernel(self):
        self.logger.info('Configure Linux kernel')
        if 'conf' in self.conf['Linux kernel']:
            psi.components.Component(self.logger,
                                     ('make', '-C', self.linux_kernel['work src tree'],
                                      'ARCH={0}'.format(self.linux_kernel['arch']),
                                      self.conf['Linux kernel']['conf'])).start()
        else:
            raise NotImplementedError('Linux kernel configuration is provided in unsupported form')

    def extract_linux_kernel_attrs(self):
        self.logger.info('Extract Linux kernel atributes')

        self.logger.debug('Get Linux kernel version')
        p = psi.components.Component(self.logger,
                                     ('make', '-s', '-C', self.linux_kernel['work src tree'], 'kernelversion'),
                                     collect_all_stdout=True)
        p.start()
        self.linux_kernel['version'] = p.stdout[0]
        self.logger.debug('Linux kernel version is "{0}"'.format(self.linux_kernel['version']))

        self.logger.debug('Get Linux kernel architecture')
        self.linux_kernel['arch'] = self.conf['Linux kernel'].get('arch') or self.conf['sys']['arch']
        self.logger.debug('Linux kernel architecture is "{0}"'.format(self.linux_kernel['arch']))

        self.logger.debug('Get Linux kernel configuration shortcut')
        self.linux_kernel['conf shortcut'] = self.conf['Linux kernel']['conf']
        self.logger.debug('Linux kernel configuration shortcut is "{0}"'.format(self.linux_kernel['conf shortcut']))

        self.linux_kernel['attrs'] = [
            {'Linux kernel': [{'version': self.linux_kernel[attr]} for attr in ('version', 'arch', 'conf shortcut')]}]

    def fetch_linux_kernel_work_src_tree(self):
        self.linux_kernel['work src tree'] = os.path.relpath(os.path.join(self.conf['root id'], 'linux'))

        self.logger.info('Fetch Linux kernel working source tree to "{0}"'.format(self.linux_kernel['work src tree']))

        self.linux_kernel['src'] = self.conf['Linux kernel']['src']

        o = urllib.parse.urlparse(self.linux_kernel['src'])
        if o[0] in ('http', 'https', 'ftp'):
            raise NotImplementedError(
                'Linux kernel source code is likely provided in unsopported form of remote archive')
        elif o[0] == 'git':
            raise NotImplementedError(
                'Linux kernel source code is likely provided in unsopported form of Git repository')
        elif o[0]:
            raise ValueError('Linux kernel source code is provided in unsupported form "{0}"'.format(o[0]))

        self.linux_kernel['src'] = psi.utils.find_file_or_dir(self.logger, self.conf['root id'],
                                                              self.linux_kernel['src'])

        if os.path.isdir(self.linux_kernel['src']):
            self.logger.debug('Linux kernel source code is provided in form of source tree')
            if self.conf['allow local source directories use']:
                os.symlink(os.path.abspath(self.linux_kernel['src']), self.linux_kernel['work src tree'])
            else:
                shutil.copytree(self.linux_kernel['src'], self.linux_kernel['work src tree'])
        elif os.path.isfile(self.linux_kernel['src']):
            self.logger.debug('Linux kernel source code is provided in form of archive')
            with tarfile.open(self.linux_kernel['src']) as TarFile:
                TarFile.extractall(self.linux_kernel['work src tree'])

    def make_canonical_linux_kernel_work_src_tree(self):
        self.logger.info('Make canonical Linux kernel working source tree')

        linux_kernel_work_src_tree_root = None

        for dirpath, dirnames, filenames in os.walk(self.linux_kernel['work src tree']):
            if psi.utils.is_src_tree_root(filenames):
                linux_kernel_work_src_tree_root = dirpath
                break

        if not linux_kernel_work_src_tree_root:
            raise ValueError('Could not find Makefile in Linux kernel source code')

        # TODO: specification requires to remove everything in self.linux_kernel['work src tree'] except moved linux_kernel_work_src_tree_root.
        if not os.path.samefile(linux_kernel_work_src_tree_root, self.linux_kernel['work src tree']):
            self.logger.debug(
                'Move "{0}" to "{1}"'.format(linux_kernel_work_src_tree_root, self.linux_kernel['work src tree']))
            os.rename(linux_kernel_work_src_tree_root, self.linux_kernel['work src tree'])

    def process_all_linux_kernel_raw_build_cmds(self):
        self.logger.info('Process all Linux kernel raw build commands')

        # It looks quite reasonable to scan Linux kernel raw build commands file once a second since build isn't
        # performed neither too fast nor too slow.
        # Offset is used to scan just new lines from Linux kernel raw build commands file.
        offset = 0
        while True:
            time.sleep(1)

            with open(self.linux_kernel['raw build cmds file']) as fp:
                try:
                    fcntl.flock(fp, fcntl.LOCK_EX)

                    # Move to previous end of file.
                    fp.seek(offset)

                    # Read new lines from file.
                    cmd = None
                    opts = []
                    prev_line = None
                    for line in fp:
                        if line == psi.lkbce.cmds.cmds.Command.cmds_separator:
                            if prev_line == psi.lkbce.cmds.cmds.Command.cmds_separator:
                                self.logger.debug('Linux kernel raw build commands "message queue" was terminated')
                                exit(0)
                            else:
                                self.logger.info('Process Linux kernel raw build command "{0}"'.format(cmd))

                                cmd_in_files = []
                                cmd_out_file = None
                                cmd_opts = []

                                if cmd == 'CC':
                                    # We assume that CC options always start with "-" and following CC options always
                                    # require values that can be specified either together with option itself (maybe
                                    # separated with "=") or by means of the following option.
                                    # Value of -o is CC output file.
                                    # The rest options are CC input files.
                                    opts_with_vals = ('D', 'O', 'mcmodel', 'o', 'x')
                                    skip_next_opt = False
                                    for idx, opt in enumerate(opts):
                                        if skip_next_opt:
                                            skip_next_opt = False
                                            continue

                                        # Options with values.
                                        match = None
                                        for opt_with_val in opts_with_vals:
                                            match = re.search(r'^-({0})=?(.*)'.format(opt_with_val), opt)
                                            if match:
                                                opt, val = match.groups()

                                                # Option value is specified by means of the following option.
                                                if not val:
                                                    val = opts[idx + 1]
                                                    skip_next_opt = True

                                                if opt == 'o':
                                                    cmd_out_file = val
                                                else:
                                                    cmd_opts.extend(['-{0}'.format(opt), val])

                                                break

                                        if not match:
                                            # Options without values.
                                            if re.search(r'^-.+$', opt):
                                                cmd_opts.append(opt)
                                            # Input files.
                                            else:
                                                cmd_in_files.append(opt)
                                elif cmd == 'LD':
                                    # We assume that LD options always have such the form:
                                    #     [-opt]... -o out_file in_file...
                                    for idx, opt in enumerate(opts):
                                        if opt == '-o':
                                            idx += 1
                                            cmd_out_file = opts[idx]
                                            while True:
                                                idx += 1
                                                try:
                                                    cmd_in_files.append(opts[idx])
                                                except IndexError:
                                                    break
                                            break
                                        else:
                                            cmd_opts.append(opt)
                                elif cmd == 'MV':
                                    # We assume that MV options always have such the form:
                                    #     [-opt]... in_file out_file
                                    for opt in opts:
                                        if re.search(r'^-', opt):
                                            cmd_opts.append(opt)
                                        elif not cmd_in_files:
                                            cmd_in_files.append(opt)
                                        else:
                                            cmd_out_file = opt
                                else:
                                    raise NotImplementedError(
                                        'Linux kernel raw build command "{0}" is not supported yet'.format(cmd))

                                # Input files and output files should be presented always.
                                if not cmd_in_files:
                                    raise ValueError(
                                        'Could not get Linux kernel raw build command input files from options "{0}"'.format(
                                            opts))
                                if not cmd_out_file:
                                    raise ValueError(
                                        'Could not get Linux kernel raw build command output file from options "{0}"'.format(
                                            opts))

                                # TODO: check that all options were parsed.
                                # if set(opts) != set(cmd_in_files + [cmd_out_file] + cmd_opts):
                                #     raise RuntimeError(
                                #         'Some options were not parsed properly: "{0} != {1} + {2} + {3}"'.format(opts,
                                #                                                                                  cmd_in_files,
                                #                                                                                  cmd_out_file,
                                #                                                                                  cmd_opts))

                                self.logger.debug(
                                    'Linux kernel raw build command input files are "{0}"'.format(cmd_in_files))
                                self.logger.debug(
                                    'Linux kernel raw build command output file is "{0}"'.format(cmd_out_file))
                                self.logger.debug('Linux kernel raw build command options are "{0}"'.format(cmd_opts))

                                cmd = None
                                opts = []
                        else:
                            if not cmd:
                                cmd = line.rstrip()
                            else:
                                opts.append(line.rstrip())

                        prev_line = line

                    # Move offset to current end of file.
                    offset = fp.tell()
                finally:
                    fcntl.flock(fp, fcntl.LOCK_UN)
